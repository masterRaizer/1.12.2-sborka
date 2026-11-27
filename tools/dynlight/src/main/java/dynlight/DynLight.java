package dynlight;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderGlobal;
import net.minecraft.client.settings.KeyBinding;
import net.minecraft.command.CommandBase;
import net.minecraft.command.ICommandSender;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityList;
import net.minecraft.entity.EntityLivingBase;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.ResourceLocation;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.text.TextComponentString;
import net.minecraft.world.World;
import net.minecraftforge.client.ClientCommandHandler;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.config.Config;
import net.minecraftforge.common.config.ConfigManager;
import net.minecraftforge.fml.client.event.ConfigChangedEvent;
import net.minecraftforge.fml.client.registry.ClientRegistry;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.lwjgl.input.Keyboard;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Client-side dynamic light. Once per client tick collects glowing things near the camera (items in hands of
 * players and mobs, dropped glowing items, burning entities), publishes them to {@link LightSources} and marks the
 * chunk sections whose light changed for a re-mesh. The world's light data is never changed, so nothing is saved,
 * mobs still spawn as before and the server knows nothing about it. No entity capabilities are attached.
 */
@Mod(modid = Tags.MOD_ID, name = Tags.MOD_NAME, version = Tags.VERSION, clientSideOnly = true,
        acceptableRemoteVersions = "*", acceptedMinecraftVersions = "[1.12.2]")
public class DynLight {

    static final Logger LOG = LogManager.getLogger("dynlight");

    @Config(modid = Tags.MOD_ID, name = "dynlight")
    public static class Cfg {
        @Config.Comment("Master switch. false = no dynamic light at all.")
        public static boolean enabled = true;
        @Config.Comment("Light from glowing items in the hands of players and mobs.")
        public static boolean heldItems = true;
        @Config.Comment("Light from glowing items lying on the ground.")
        public static boolean droppedItems = true;
        @Config.Comment("Light from burning entities (mobs, players, arrows on fire).")
        public static boolean burningEntities = true;
        @Config.Comment("Brightness of a burning entity, 0-15.")
        @Config.RangeInt(min = 0, max = 15)
        public static int burningLight = 14;
        @Config.Comment("Sources farther than this from the camera are ignored (blocks).")
        @Config.RangeInt(min = 8, max = 128)
        public static int maxDistance = 48;
        @Config.Comment("At most this many nearest sources light the world at once.")
        @Config.RangeInt(min = 1, max = 256)
        public static int maxSources = 32;
        @Config.Comment("Terrain light is re-meshed at most once per this many ticks (1 = smoothest, 4 = cheapest).")
        @Config.RangeInt(min = 1, max = 20)
        public static int terrainUpdateTicks = 2;
        @Config.Comment({"Items that glow although they are not blocks, or a different brightness: modid:item=N or",
                "modid:item@meta=N (N 0-15, 0 turns an item off). Blocks glow by themselves (torch 14, glowstone 15)."})
        public static String[] itemLight = {
                "minecraft:glowstone_dust=10",
                "minecraft:lava_bucket=15",
                "minecraft:blaze_rod=10",
                "minecraft:blaze_powder=8",
                "minecraft:magma_cream=8",
                "minecraft:nether_star=12",
        };
        @Config.Comment("Entities that always glow: modid:entity=N.")
        public static String[] entityLight = {
                "minecraft:blaze=10",
        };
    }

    private static KeyBinding toggleKey;
    private static final Map<Class<?>, Integer> ENTITY_CACHE = new HashMap<>();
    private static final Map<String, Integer> ENTITY_LIGHT = new HashMap<>();

    /** Sources the terrain was last meshed with: {bx, by, bz, lum} per source. */
    private static int[] meshed = new int[0];
    private static World lastWorld;
    private static int tick;

    private double[] buf = new double[64];
    private double[] dist = new double[16];

    @Mod.EventHandler
    public void init(FMLInitializationEvent event) {
        reloadConfig();
        MinecraftForge.EVENT_BUS.register(this);
        toggleKey = new KeyBinding("key.dynlight.toggle", Keyboard.KEY_NONE, "key.categories.misc");
        ClientRegistry.registerKeyBinding(toggleKey);
        ClientCommandHandler.instance.registerCommand(new Cmd());
    }

    static void reloadConfig() {
        ItemLight.reload(Cfg.itemLight, LOG);
        ENTITY_CACHE.clear();
        ENTITY_LIGHT.clear();
        if (Cfg.entityLight != null) {
            for (String line : Cfg.entityLight) {
                int eq = line == null ? -1 : line.lastIndexOf('=');
                if (eq <= 0) {
                    continue;
                }
                try {
                    ENTITY_LIGHT.put(line.substring(0, eq).trim(),
                            Math.max(0, Math.min(15, Integer.parseInt(line.substring(eq + 1).trim()))));
                } catch (NumberFormatException e) {
                    LOG.warn("Bad entity light line '{}', skipped", line);
                }
            }
        }
    }

    @SubscribeEvent
    public void onConfigChanged(ConfigChangedEvent.OnConfigChangedEvent event) {
        if (Tags.MOD_ID.equals(event.getModID())) {
            ConfigManager.sync(Tags.MOD_ID, Config.Type.INSTANCE);
            reloadConfig();
        }
    }

    @SubscribeEvent
    public void onKey(InputEvent.KeyInputEvent event) {
        if (toggleKey != null && toggleKey.isPressed()) {
            setEnabled(!Cfg.enabled);
            Minecraft mc = Minecraft.getMinecraft();
            if (mc.player != null) {
                mc.player.sendStatusMessage(new TextComponentString("Dynamic light: " + (Cfg.enabled ? "on" : "off")), true);
            }
        }
    }

    static void setEnabled(boolean on) {
        Cfg.enabled = on;
        ConfigManager.sync(Tags.MOD_ID, Config.Type.INSTANCE);
    }

    @SubscribeEvent
    public void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        try {
            update();
        } catch (Throwable t) {
            // never crash the game for a visual effect: switch the light off for this session and say why once
            LOG.error("Dynamic light failed and is off until restart", t);
            Cfg.enabled = false;
            LightSources.snapshot = LightSources.EMPTY;
            meshed = new int[0];
        }
    }

    private void update() {
        Minecraft mc = Minecraft.getMinecraft();
        World world = mc.world;
        if (world != lastWorld) {
            // new world or dimension: the old sources belong to meshes that no longer exist
            lastWorld = world;
            meshed = new int[0];
            LightSources.snapshot = LightSources.EMPTY;
        }
        Entity cam = mc.getRenderViewEntity();
        if (world == null || cam == null) {
            return;
        }
        int count = 0;
        if (Cfg.enabled) {
            count = collect(world, cam);
        }
        double[] snap = count == 0 ? LightSources.EMPTY : Arrays.copyOf(buf, count * 4);
        LightSources.snapshot = snap;

        if (++tick % Math.max(1, Cfg.terrainUpdateTicks) == 0 || (count == 0 && meshed.length > 0)) {
            remesh(mc.renderGlobal, snap);
        }
    }

    /** Fills {@link #buf} with the nearest sources, returns how many. */
    private int collect(World world, Entity cam) {
        double maxD = Cfg.maxDistance;
        double maxD2 = maxD * maxD;
        int n = 0;
        List<Entity> list = world.loadedEntityList;
        for (int i = 0, size = list.size(); i < size; i++) {
            Entity e = list.get(i);
            if (e == null || e.isDead) {
                continue;
            }
            double d2 = e.getDistanceSq(cam.posX, cam.posY, cam.posZ);
            if (d2 > maxD2) {
                continue;
            }
            int lum = 0;
            double y = e.posY + e.height * 0.5D;
            if (e instanceof EntityItem) {
                if (Cfg.droppedItems) {
                    lum = ItemLight.of(((EntityItem) e).getItem(), false);
                    y = e.posY + 0.25D;
                }
            } else if (e instanceof EntityLivingBase) {
                if (e instanceof EntityPlayer && ((EntityPlayer) e).isSpectator()) {
                    continue;
                }
                if (Cfg.heldItems) {
                    EntityLivingBase living = (EntityLivingBase) e;
                    boolean fluids = e instanceof EntityPlayer;
                    lum = Math.max(ItemLight.of(living.getHeldItemMainhand(), fluids),
                            ItemLight.of(living.getHeldItemOffhand(), fluids));
                    if (lum > 0) {
                        y = e.posY + e.getEyeHeight() - 0.3D;
                    }
                }
            }
            if (Cfg.burningEntities && Cfg.burningLight > lum && e.isBurning()) {
                lum = Cfg.burningLight;
                y = e.posY + e.height * 0.5D;
            }
            int fixed = entityLight(e);
            if (fixed > lum) {
                lum = fixed;
                y = e.posY + e.height * 0.5D;
            }
            if (lum <= 0) {
                continue;
            }
            n = insert(n, e.posX, y, e.posZ, lum, d2);
        }
        return n;
    }

    /** Keeps the {@code maxSources} nearest sources in {@link #buf}, sorted by distance. */
    private int insert(int n, double x, double y, double z, double lum, double d2) {
        int max = Math.max(1, Cfg.maxSources);
        if (buf.length < max * 4) {
            buf = Arrays.copyOf(buf, max * 4);
        }
        if (dist.length < max) {
            dist = Arrays.copyOf(dist, max);
        }
        if (n > max) {
            n = max;
        }
        int pos = n;
        if (n >= max) {
            if (d2 >= dist[max - 1]) {
                return n;
            }
            pos = max - 1;
        }
        while (pos > 0 && dist[pos - 1] > d2) {
            dist[pos] = dist[pos - 1];
            System.arraycopy(buf, (pos - 1) * 4, buf, pos * 4, 4);
            pos--;
        }
        dist[pos] = d2;
        buf[pos * 4] = x;
        buf[pos * 4 + 1] = y;
        buf[pos * 4 + 2] = z;
        buf[pos * 4 + 3] = lum;
        return Math.min(n + 1, max);
    }

    private static int entityLight(Entity e) {
        if (ENTITY_LIGHT.isEmpty()) {
            return 0;
        }
        Class<?> c = e.getClass();
        Integer v = ENTITY_CACHE.get(c);
        if (v == null) {
            ResourceLocation rl = EntityList.getKey(e);
            v = rl == null ? null : ENTITY_LIGHT.get(rl.toString());
            if (v == null) {
                v = 0;
            }
            ENTITY_CACHE.put(c, v);
        }
        return v;
    }

    /** Marks for re-mesh every chunk section touched by a source that appeared, moved, changed or went away. */
    private static void remesh(RenderGlobal rg, double[] snap) {
        int n = snap.length / 4;
        int[] now = new int[n * 4];
        for (int i = 0; i < n; i++) {
            now[i * 4] = floor(snap[i * 4]);
            now[i * 4 + 1] = floor(snap[i * 4 + 1]);
            now[i * 4 + 2] = floor(snap[i * 4 + 2]);
            now[i * 4 + 3] = (int) Math.ceil(snap[i * 4 + 3]);
        }
        int[] old = meshed;
        meshed = now;
        if (rg == null) {
            return;
        }
        Set<Long> sections = new HashSet<>();
        addChanged(now, old, sections);
        addChanged(old, now, sections);
        for (Long key : sections) {
            BlockPos s = BlockPos.fromLong(key);
            int x = s.getX() << 4;
            int y = s.getY() << 4;
            int z = s.getZ() << 4;
            // RenderGlobal widens the range by one block on each side, so the inner box hits exactly this section
            rg.markBlockRangeForRenderUpdate(x + 1, y + 1, z + 1, x + 14, y + 14, z + 14);
        }
    }

    /** Adds the sections of every source in {@code a} that is not in {@code b}. */
    private static void addChanged(int[] a, int[] b, Set<Long> out) {
        outer:
        for (int i = 0; i < a.length; i += 4) {
            for (int j = 0; j < b.length; j += 4) {
                if (a[i] == b[j] && a[i + 1] == b[j + 1] && a[i + 2] == b[j + 2] && a[i + 3] == b[j + 3]) {
                    continue outer;
                }
            }
            int r = a[i + 3];
            int sx0 = (a[i] - r) >> 4, sx1 = (a[i] + r) >> 4;
            int sy0 = Math.max(0, (a[i + 1] - r) >> 4), sy1 = Math.min(15, (a[i + 1] + r) >> 4);
            int sz0 = (a[i + 2] - r) >> 4, sz1 = (a[i + 2] + r) >> 4;
            for (int sx = sx0; sx <= sx1; sx++) {
                for (int sy = sy0; sy <= sy1; sy++) {
                    for (int sz = sz0; sz <= sz1; sz++) {
                        out.add(new BlockPos(sx, sy, sz).toLong());
                    }
                }
            }
        }
    }

    private static int floor(double v) {
        int i = (int) v;
        return v < i ? i - 1 : i;
    }

    /** Client command: /dynlight [on|off|status]. */
    private static final class Cmd extends CommandBase {
        @Override
        public String getName() {
            return "dynlight";
        }

        @Override
        public String getUsage(ICommandSender sender) {
            return "/dynlight [on|off|status]";
        }

        @Override
        public int getRequiredPermissionLevel() {
            return 0;
        }

        @Override
        public boolean checkPermission(MinecraftServer server, ICommandSender sender) {
            return true;
        }

        @Override
        public void execute(MinecraftServer server, ICommandSender sender, String[] args) {
            if (args.length > 0 && "on".equalsIgnoreCase(args[0])) {
                setEnabled(true);
            } else if (args.length > 0 && "off".equalsIgnoreCase(args[0])) {
                setEnabled(false);
            }
            sender.sendMessage(new TextComponentString("Dynamic light: " + (Cfg.enabled ? "on" : "off")
                    + ", sources " + (LightSources.snapshot.length / 4)));
        }
    }
}
