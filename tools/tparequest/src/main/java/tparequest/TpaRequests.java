package tparequest;

import net.minecraft.command.CommandBase;
import net.minecraft.command.ICommandSender;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.text.ITextComponent;
import net.minecraft.util.text.TextComponentString;
import net.minecraft.util.text.TextFormatting;
import net.minecraft.util.text.event.ClickEvent;
import net.minecraft.util.text.event.HoverEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.config.Config;
import net.minecraftforge.common.config.ConfigManager;
import net.minecraftforge.fml.client.event.ConfigChangedEvent;
import net.minecraftforge.fml.common.FMLCommonHandler;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLServerStartingEvent;
import net.minecraftforge.fml.common.event.FMLServerStoppingEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.PlayerEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Server-side only. /tpa, /tpahere, /tpaccept, /tpadeny, /tpacancel for all players (no op needed),
 * with clickable [✔] / [✖] buttons in chat and a request timeout. Vanilla clients see the buttons too.
 */
@Mod(modid = Tags.MOD_ID, name = Tags.MOD_NAME, version = Tags.VERSION, acceptableRemoteVersions = "*")
public class TpaRequests {

    static final Logger LOG = LogManager.getLogger("tparequest");

    @Config(modid = Tags.MOD_ID)
    public static class Cfg {
        @Config.Comment("Turn the /tpa commands on/off (needs a server restart)")
        public static boolean enabled = true;

        @Config.Comment("Seconds a request waits for an answer before it expires")
        @Config.RangeInt(min = 5, max = 3600)
        public static int timeoutSeconds = 60;

        @Config.Comment("Allow /tpahere (ask another player to come to you)")
        public static boolean allowTpaHere = true;

        @Config.Comment("Allow teleporting to a player who is in another dimension")
        public static boolean allowCrossDimension = true;
    }

    /** One pending request. from = who sent it; mover = who will be teleported. */
    static final class Request {
        final UUID from, to;
        final String fromName, toName;
        final boolean here; // true: /tpahere, the target comes to the sender
        final long expiresAt;

        Request(EntityPlayerMP from, EntityPlayerMP to, boolean here) {
            this.from = from.getUniqueID();
            this.to = to.getUniqueID();
            this.fromName = from.getName();
            this.toName = to.getName();
            this.here = here;
            this.expiresAt = System.currentTimeMillis() + Cfg.timeoutSeconds * 1000L;
        }
    }

    /** Outgoing requests, one per sender (a new request replaces the old one). Insertion order = age. */
    static final Map<UUID, Request> REQUESTS = new LinkedHashMap<>();
    private int ticks;

    @Mod.EventHandler
    public void init(FMLInitializationEvent e) {
        MinecraftForge.EVENT_BUS.register(this);
    }

    @Mod.EventHandler
    public void serverStarting(FMLServerStartingEvent e) {
        REQUESTS.clear();
        if (!Cfg.enabled) {
            LOG.info("TPA commands are disabled in config");
            return;
        }
        e.registerServerCommand(new CmdTpa("tpa", false));
        e.registerServerCommand(new CmdTpa("tpahere", true));
        e.registerServerCommand(new CmdAnswer("tpaccept", true));
        e.registerServerCommand(new CmdAnswer("tpadeny", false));
        e.registerServerCommand(new CmdCancel());
        LOG.info("TPA commands registered: tpa, tpahere, tpaccept, tpadeny, tpacancel (timeout {} s)", Cfg.timeoutSeconds);
    }

    @Mod.EventHandler
    public void serverStopping(FMLServerStoppingEvent e) {
        REQUESTS.clear();
    }

    @SubscribeEvent
    public void onConfigChanged(ConfigChangedEvent.OnConfigChangedEvent e) {
        if (Tags.MOD_ID.equals(e.getModID())) ConfigManager.sync(Tags.MOD_ID, Config.Type.INSTANCE);
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || REQUESTS.isEmpty() || ++ticks < 20) return;
        ticks = 0;
        long now = System.currentTimeMillis();
        MinecraftServer server = FMLCommonHandler.instance().getMinecraftServerInstance();
        Iterator<Request> it = REQUESTS.values().iterator();
        while (it.hasNext()) {
            Request r = it.next();
            if (r.expiresAt > now) continue;
            it.remove();
            send(server, r.from, msg(TextFormatting.GRAY, "Запрос к игроку " + r.toName + " истёк."));
            send(server, r.to, msg(TextFormatting.GRAY, "Запрос от игрока " + r.fromName + " истёк."));
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent e) {
        UUID id = e.player.getUniqueID();
        MinecraftServer server = FMLCommonHandler.instance().getMinecraftServerInstance();
        Iterator<Request> it = REQUESTS.values().iterator();
        while (it.hasNext()) {
            Request r = it.next();
            if (r.from.equals(id)) {
                it.remove();
                send(server, r.to, msg(TextFormatting.GRAY, "Запрос от игрока " + r.fromName + " отменён: игрок вышел с сервера."));
            } else if (r.to.equals(id)) {
                it.remove();
                send(server, r.from, msg(TextFormatting.GRAY, "Запрос к игроку " + r.toName + " отменён: игрок вышел с сервера."));
            }
        }
    }

    // ---------- chat helpers ----------

    static ITextComponent msg(TextFormatting color, String text) {
        ITextComponent prefix = new TextComponentString("[TPA] ");
        prefix.getStyle().setColor(TextFormatting.GOLD);
        ITextComponent body = new TextComponentString(text);
        body.getStyle().setColor(color);
        return prefix.appendSibling(body);
    }

    static ITextComponent button(String label, TextFormatting color, String command, String hint) {
        ITextComponent b = new TextComponentString(label);
        ITextComponent hover = new TextComponentString(hint + "\n");
        ITextComponent cmd = new TextComponentString(command);
        cmd.getStyle().setColor(TextFormatting.YELLOW);
        hover.appendSibling(cmd);
        b.getStyle().setColor(color).setBold(true)
                .setClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, command))
                .setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, hover));
        return b;
    }

    static void send(MinecraftServer server, UUID id, ITextComponent text) {
        if (server == null) return;
        EntityPlayerMP p = server.getPlayerList().getPlayerByUUID(id);
        if (p != null) p.sendMessage(text);
    }

    static EntityPlayerMP online(MinecraftServer server, UUID id) {
        return server.getPlayerList().getPlayerByUUID(id);
    }

    // ---------- teleport ----------

    static void teleport(EntityPlayerMP mover, EntityPlayerMP dest) {
        final double x = dest.posX, y = dest.posY, z = dest.posZ;
        final float yaw = dest.rotationYaw, pitch = dest.rotationPitch;
        if (mover.isPlayerSleeping()) mover.wakeUpPlayer(true, true, false);
        if (mover.isRiding()) mover.dismountRidingEntity();
        mover.removePassengers();
        if (mover.dimension != dest.dimension) {
            mover.changeDimension(dest.dimension, (world, entity, y2) ->
                    entity.setLocationAndAngles(x, y, z, yaw, pitch));
        }
        mover.motionX = mover.motionY = mover.motionZ = 0;
        mover.fallDistance = 0;
        mover.connection.setPlayerLocation(x, y, z, yaw, pitch);
    }

    // ---------- commands ----------

    abstract static class PlayerCmd extends CommandBase {
        @Override
        public int getRequiredPermissionLevel() {
            return 0;
        }

        /** Every player may use it, not only ops (vanilla only lets non-ops use a few built-in commands). */
        @Override
        public boolean checkPermission(MinecraftServer server, ICommandSender sender) {
            return sender instanceof EntityPlayerMP;
        }

        @Override
        public void execute(MinecraftServer server, ICommandSender sender, String[] args) {
            if (!(sender instanceof EntityPlayerMP)) {
                sender.sendMessage(new TextComponentString("Only players can use this command"));
                return;
            }
            run(server, (EntityPlayerMP) sender, args);
        }

        abstract void run(MinecraftServer server, EntityPlayerMP me, String[] args);
    }

    /** /tpa <player> and /tpahere <player>. */
    static final class CmdTpa extends PlayerCmd {
        private final String name;
        private final boolean here;

        CmdTpa(String name, boolean here) {
            this.name = name;
            this.here = here;
        }

        @Override
        public String getName() {
            return name;
        }

        @Override
        public String getUsage(ICommandSender sender) {
            return "/" + name + " <ник>";
        }

        @Override
        public List<String> getTabCompletions(MinecraftServer server, ICommandSender sender, String[] args, BlockPos pos) {
            return args.length == 1 ? getListOfStringsMatchingLastWord(args, server.getOnlinePlayerNames()) : Collections.<String>emptyList();
        }

        @Override
        public boolean isUsernameIndex(String[] args, int index) {
            return index == 0;
        }

        @Override
        void run(MinecraftServer server, EntityPlayerMP me, String[] args) {
            if (here && !Cfg.allowTpaHere) {
                me.sendMessage(msg(TextFormatting.RED, "Команда /tpahere выключена на сервере."));
                return;
            }
            if (args.length != 1) {
                me.sendMessage(msg(TextFormatting.RED, "Использование: /" + name + " <ник>"));
                return;
            }
            EntityPlayerMP target = server.getPlayerList().getPlayerByUsername(args[0]);
            if (target == null) {
                me.sendMessage(msg(TextFormatting.RED, "Игрок " + args[0] + " не в сети."));
                return;
            }
            if (target == me) {
                me.sendMessage(msg(TextFormatting.RED, "Нельзя отправить запрос самому себе."));
                return;
            }
            if (!Cfg.allowCrossDimension && target.dimension != me.dimension) {
                me.sendMessage(msg(TextFormatting.RED, "Игрок " + target.getName() + " в другом измерении, а телепорт между измерениями выключен."));
                return;
            }
            Request old = REQUESTS.remove(me.getUniqueID());
            if (old != null && !old.to.equals(target.getUniqueID())) {
                send(server, old.to, msg(TextFormatting.GRAY, "Игрок " + old.fromName + " отменил запрос."));
            }
            Request r = new Request(me, target, here);
            REQUESTS.put(me.getUniqueID(), r);

            String accept = "/tpaccept " + me.getName();
            String deny = "/tpadeny " + me.getName();
            target.sendMessage(msg(TextFormatting.YELLOW, here
                    ? "Игрок " + me.getName() + " зовёт вас телепортироваться к нему."
                    : "Игрок " + me.getName() + " хочет телепортироваться к вам."));
            ITextComponent line = new TextComponentString("      ");
            line.appendSibling(button("[✔ Принять]", TextFormatting.GREEN, accept, "Нажмите, чтобы принять, или введите:"));
            line.appendSibling(new TextComponentString("   "));
            line.appendSibling(button("[✖ Отклонить]", TextFormatting.RED, deny, "Нажмите, чтобы отклонить, или введите:"));
            target.sendMessage(line);
            target.sendMessage(msg(TextFormatting.GRAY, "Или введите /tpaccept или /tpadeny. Запрос действует " + Cfg.timeoutSeconds + " с."));

            ITextComponent sent = msg(TextFormatting.YELLOW, "Запрос отправлен игроку " + target.getName() + ". ");
            sent.appendSibling(button("[✖ Отменить]", TextFormatting.RED, "/tpacancel", "Нажмите, чтобы отменить, или введите:"));
            me.sendMessage(sent);
        }
    }

    /** /tpaccept [player] and /tpadeny [player]. Without a name: the newest request to me. */
    static final class CmdAnswer extends PlayerCmd {
        private final String name;
        private final boolean accept;

        CmdAnswer(String name, boolean accept) {
            this.name = name;
            this.accept = accept;
        }

        @Override
        public String getName() {
            return name;
        }

        @Override
        public List<String> getAliases() {
            // the owner types "/tpaacept" (double a) - accept it too
            return accept ? Collections.singletonList("tpaacept") : Collections.<String>emptyList();
        }

        @Override
        public String getUsage(ICommandSender sender) {
            return "/" + name + " [ник]";
        }

        @Override
        public List<String> getTabCompletions(MinecraftServer server, ICommandSender sender, String[] args, BlockPos pos) {
            if (args.length != 1 || !(sender instanceof EntityPlayerMP)) return Collections.emptyList();
            UUID me = ((EntityPlayerMP) sender).getUniqueID();
            List<String> names = new ArrayList<>();
            for (Request r : REQUESTS.values()) if (r.to.equals(me)) names.add(r.fromName);
            return getListOfStringsMatchingLastWord(args, names);
        }

        @Override
        void run(MinecraftServer server, EntityPlayerMP me, String[] args) {
            Request found = null;
            for (Request r : REQUESTS.values()) {
                if (!r.to.equals(me.getUniqueID())) continue;
                if (args.length == 0 || r.fromName.equalsIgnoreCase(args[0])) found = r; // keeps the newest
            }
            if (found == null) {
                me.sendMessage(msg(TextFormatting.RED, args.length == 0
                        ? "У вас нет входящих запросов на телепорт."
                        : "Нет запроса от игрока " + args[0] + "."));
                return;
            }
            REQUESTS.remove(found.from);
            EntityPlayerMP from = online(server, found.from);
            if (from == null) {
                me.sendMessage(msg(TextFormatting.RED, "Игрок " + found.fromName + " уже не в сети."));
                return;
            }
            if (!accept) {
                me.sendMessage(msg(TextFormatting.GRAY, "Вы отклонили запрос игрока " + from.getName() + "."));
                from.sendMessage(msg(TextFormatting.RED, "Игрок " + me.getName() + " отклонил ваш запрос."));
                return;
            }
            EntityPlayerMP mover = found.here ? me : from;
            EntityPlayerMP dest = found.here ? from : me;
            if (!mover.isEntityAlive() || !dest.isEntityAlive()) {
                me.sendMessage(msg(TextFormatting.RED, "Сейчас телепорт невозможен: игрок мёртв."));
                from.sendMessage(msg(TextFormatting.RED, "Сейчас телепорт невозможен: игрок мёртв."));
                return;
            }
            if (!Cfg.allowCrossDimension && mover.dimension != dest.dimension) {
                me.sendMessage(msg(TextFormatting.RED, "Игроки в разных измерениях, а телепорт между измерениями выключен."));
                from.sendMessage(msg(TextFormatting.RED, "Игроки в разных измерениях, а телепорт между измерениями выключен."));
                return;
            }
            me.sendMessage(msg(TextFormatting.GREEN, "Вы приняли запрос игрока " + from.getName() + "."));
            from.sendMessage(msg(TextFormatting.GREEN, "Игрок " + me.getName() + " принял ваш запрос."));
            teleport(mover, dest);
            LOG.info("{} teleported to {} (dim {})", mover.getName(), dest.getName(), dest.dimension);
        }
    }

    /** /tpacancel: cancel my outgoing request. */
    static final class CmdCancel extends PlayerCmd {
        @Override
        public String getName() {
            return "tpacancel";
        }

        @Override
        public String getUsage(ICommandSender sender) {
            return "/tpacancel";
        }

        @Override
        void run(MinecraftServer server, EntityPlayerMP me, String[] args) {
            Request r = REQUESTS.remove(me.getUniqueID());
            if (r == null) {
                me.sendMessage(msg(TextFormatting.RED, "У вас нет отправленных запросов."));
                return;
            }
            me.sendMessage(msg(TextFormatting.GRAY, "Запрос к игроку " + r.toName + " отменён."));
            send(server, r.to, msg(TextFormatting.GRAY, "Игрок " + r.fromName + " отменил запрос."));
        }
    }
}
