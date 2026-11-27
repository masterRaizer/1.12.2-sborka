package lootclear;

import net.minecraft.command.CommandBase;
import net.minecraft.command.CommandException;
import net.minecraft.command.ICommandSender;
import net.minecraft.command.WrongUsageException;
import net.minecraft.entity.Entity;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.item.EntityXPOrb;
import net.minecraft.item.ItemStack;
import net.minecraft.nbt.NBTTagCompound;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.ResourceLocation;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.text.TextComponentString;
import net.minecraft.world.WorldServer;
import net.minecraftforge.common.DimensionManager;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.config.Config;
import net.minecraftforge.common.config.ConfigManager;
import net.minecraftforge.event.entity.player.PlayerDropsEvent;
import net.minecraftforge.fml.client.event.ConfigChangedEvent;
import net.minecraftforge.fml.common.FMLCommonHandler;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLServerStartingEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Server-side only. Every N minutes removes dropped items (EntityItem) lying in loaded chunks, with chat warnings
 * before it. Item frames, armor stands and other entities are never touched. Works in single player too.
 */
@Mod(modid = Tags.MOD_ID, name = Tags.MOD_NAME, version = Tags.VERSION, acceptableRemoteVersions = "*")
public class LootClear {

    private static final Logger LOG = LogManager.getLogger("lootclear");
    static final String DEATH_TAG = "lootclear_death";

    private int ticks;
    private int secondsLeft = -1;

    @Config(modid = Tags.MOD_ID)
    public static class Cfg {
        @Config.Comment("Turn automatic loot clearing on/off")
        public static boolean enabled = true;

        @Config.Comment("Minutes between clears")
        @Config.RangeInt(min = 1, max = 1440)
        public static int intervalMinutes = 10;

        @Config.Comment("Seconds before the clear when a chat warning is shown")
        public static int[] warnSeconds = {180, 60, 3, 2, 1};

        @Config.Comment("Warnings at this many seconds or fewer use the short countdownMessage")
        @Config.RangeInt(min = 0, max = 60)
        public static int countdownFrom = 5;

        @Config.Comment("Items younger than this (seconds on the ground) are kept")
        @Config.RangeInt(min = 0, max = 3600)
        public static int minAgeSeconds = 30;

        @Config.Comment("Keep items dropped by a player's death (vanilla still despawns them after 5 minutes)")
        public static boolean protectDeathLoot = true;

        @Config.Comment("Clear only plain dropped items; special item entities of other mods (Draconic, Botania...) are kept")
        public static boolean onlyPlainItems = true;

        @Config.Comment("Keep items a mod marked as never despawning (Age -32768 or PickupDelay 32767)")
        public static boolean keepNeverDespawn = true;

        @Config.Comment("Item ids that are never cleared, e.g. minecraft:nether_star")
        public static String[] itemBlacklist = {"minecraft:dragon_egg", "minecraft:nether_star", "minecraft:elytra",
                "minecraft:beacon", "minecraft:totem_of_undying"};

        @Config.Comment("Dimension ids where nothing is cleared")
        public static int[] dimensionBlacklist = {};

        @Config.Comment("Also remove experience orbs")
        public static boolean clearXpOrbs = false;

        @Config.Comment("Warning text, %s = time like '3 минуты'. & = colour code")
        public static String warnMessage = "&e[Очистка] &fЛут будет удалён через &e%s";

        @Config.Comment("Short countdown text, %d = seconds")
        public static String countdownMessage = "&e[Очистка] &c%d";

        @Config.Comment("Text after the clear, %s = count like '12 предметов'")
        public static String doneMessage = "&e[Очистка] &aЛут очищен (%s)";
    }

    @Mod.EventHandler
    public void init(FMLInitializationEvent e) {
        MinecraftForge.EVENT_BUS.register(this);
    }

    @Mod.EventHandler
    public void serverStarting(FMLServerStartingEvent e) {
        secondsLeft = -1;
        ticks = 0;
        e.registerServerCommand(new Cmd());
    }

    @SubscribeEvent
    public void onConfigChanged(ConfigChangedEvent.OnConfigChangedEvent e) {
        if (Tags.MOD_ID.equals(e.getModID())) {
            ConfigManager.sync(Tags.MOD_ID, Config.Type.INSTANCE);
            secondsLeft = -1;
        }
    }

    @SubscribeEvent
    public void onPlayerDrops(PlayerDropsEvent e) {
        if (!Cfg.protectDeathLoot) return;
        for (EntityItem item : e.getDrops()) item.addTag(DEATH_TAG);
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !Cfg.enabled) return;
        if (++ticks < 20) return;
        ticks = 0;
        int interval = Cfg.intervalMinutes * 60;
        if (secondsLeft < 0 || secondsLeft > interval) secondsLeft = interval;
        secondsLeft--;
        try {
            if (secondsLeft <= 0) {
                secondsLeft = interval;
                broadcast(String.format(Cfg.doneMessage, count(clearNow())));
            } else if (isWarnSecond(secondsLeft)) {
                broadcast(warnText(secondsLeft));
            }
        } catch (Throwable t) {
            LOG.error("Loot clear failed", t);
        }
    }

    private static boolean isWarnSecond(int s) {
        for (int w : Cfg.warnSeconds) if (w == s) return true;
        return false;
    }

    static String warnText(int s) {
        if (s <= Cfg.countdownFrom) return String.format(Cfg.countdownMessage, s);
        return String.format(Cfg.warnMessage, timeText(s));
    }

    /** Removes matching entities in all loaded worlds, returns how many were removed. */
    static int clearNow() {
        Set<String> blacklist = new HashSet<>(Arrays.asList(Cfg.itemBlacklist));
        Set<Integer> dims = new HashSet<>();
        for (int d : Cfg.dimensionBlacklist) dims.add(d);
        int minAge = Cfg.minAgeSeconds * 20;
        int removed = 0;
        for (WorldServer w : DimensionManager.getWorlds()) {
            if (w == null || dims.contains(w.provider.getDimension())) continue;
            for (Entity ent : new ArrayList<>(w.loadedEntityList)) {
                if (ent.isDead) continue;
                if (ent instanceof EntityItem) {
                    if (shouldClear((EntityItem) ent, blacklist, minAge)) {
                        ent.setDead();
                        removed++;
                    }
                } else if (Cfg.clearXpOrbs && ent instanceof EntityXPOrb) {
                    ent.setDead();
                    removed++;
                }
            }
        }
        LOG.info("Removed {} dropped items", removed);
        return removed;
    }

    private static boolean shouldClear(EntityItem item, Set<String> blacklist, int minAge) {
        if (Cfg.onlyPlainItems && item.getClass() != EntityItem.class) return false;
        if (Cfg.protectDeathLoot && item.getTags().contains(DEATH_TAG)) return false;
        ItemStack stack = item.getItem();
        if (!stack.isEmpty()) {
            ResourceLocation id = stack.getItem().getRegistryName();
            if (id != null && blacklist.contains(id.toString())) return false;
        }
        NBTTagCompound nbt = new NBTTagCompound();
        item.writeToNBT(nbt);
        int age = nbt.getShort("Age");
        int pickupDelay = nbt.getShort("PickupDelay");
        if (Cfg.keepNeverDespawn && (age == -32768 || pickupDelay == 32767)) return false;
        return age >= minAge;
    }

    private static void broadcast(String text) {
        MinecraftServer server = FMLCommonHandler.instance().getMinecraftServerInstance();
        if (server == null) return;
        server.getPlayerList().sendMessage(new TextComponentString(text.replace('&', '§')));
    }

    static String plural(int n, String one, String few, String many) {
        int a = Math.abs(n) % 100, b = a % 10;
        if (a >= 11 && a <= 14) return many;
        if (b == 1) return one;
        if (b >= 2 && b <= 4) return few;
        return many;
    }

    static String timeText(int s) {
        if (s >= 60 && s % 60 == 0) {
            int m = s / 60;
            return m + " " + plural(m, "минуту", "минуты", "минут");
        }
        return s + " " + plural(s, "секунду", "секунды", "секунд");
    }

    static String count(int n) {
        return n + " " + plural(n, "предмет", "предмета", "предметов");
    }

    private class Cmd extends CommandBase {
        @Override
        public String getName() {
            return "lootclear";
        }

        @Override
        public String getUsage(ICommandSender sender) {
            return "/lootclear <now|time>";
        }

        @Override
        public int getRequiredPermissionLevel() {
            return 2;
        }

        @Override
        public void execute(MinecraftServer server, ICommandSender sender, String[] args) throws CommandException {
            if (args.length == 1 && "now".equals(args[0])) {
                broadcast(String.format(Cfg.doneMessage, count(clearNow())));
                secondsLeft = -1;
            } else if (args.length == 1 && "time".equals(args[0])) {
                String t = !Cfg.enabled ? "выключено" : secondsLeft < 0 ? timeText(Cfg.intervalMinutes * 60) : timeText(secondsLeft);
                sender.sendMessage(new TextComponentString("§e[Очистка] §fДо очистки: " + t));
            } else {
                throw new WrongUsageException(getUsage(sender));
            }
        }

        @Override
        public List<String> getTabCompletions(MinecraftServer server, ICommandSender sender, String[] args, BlockPos pos) {
            return args.length == 1 ? getListOfStringsMatchingLastWord(args, "now", "time") : Collections.emptyList();
        }
    }
}
