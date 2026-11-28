package chestsort;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.SidedProxy;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.PlayerEvent;
import net.minecraftforge.fml.common.network.NetworkRegistry;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.common.network.simpleimpl.SimpleNetworkWrapper;
import net.minecraftforge.fml.relauncher.Side;

/**
 * Chest Sort: a sort button and a criterion switch in container GUIs.
 * The client only computes the order (sort keys per slot); the server merges stacks and puts them back,
 * refusing whenever anything looks unsafe. Both sides need the mod; a client without it can still join.
 */
@Mod(modid = Tags.MOD_ID, name = Tags.MOD_NAME, version = Tags.VERSION, acceptableRemoteVersions = "*")
public class ChestSort {

    @SidedProxy(clientSide = "chestsort.client.ClientProxy", serverSide = "chestsort.CommonProxy")
    public static CommonProxy proxy;

    public static SimpleNetworkWrapper net;

    private static final Map<UUID, Long> lastSort = new HashMap<>();

    @Mod.EventHandler
    public void preInit(FMLPreInitializationEvent e) {
        SortConfig.load(e.getSuggestedConfigurationFile());
        net = NetworkRegistry.INSTANCE.newSimpleChannel(Tags.MOD_ID);
        net.registerMessage(SortHandler.class, MsgSort.class, 0, Side.SERVER);
        net.registerMessage(HelloHandler.class, MsgHello.class, 1, Side.CLIENT);
    }

    @Mod.EventHandler
    public void init(FMLInitializationEvent e) {
        MinecraftForge.EVENT_BUS.register(this);
        proxy.init();
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent e) {
        if (e.player instanceof EntityPlayerMP && SortConfig.serverEnabled) {
            net.sendTo(new MsgHello(SortConfig.sortHotbar, SortConfig.minContainerSlots), (EntityPlayerMP) e.player);
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent e) {
        lastSort.remove(e.player.getUniqueID());
    }

    public static class SortHandler implements IMessageHandler<MsgSort, IMessage> {
        @Override
        public IMessage onMessage(MsgSort msg, MessageContext ctx) {
            final EntityPlayerMP player = ctx.getServerHandler().player;
            if (!msg.valid || !SortConfig.serverEnabled) return null;
            player.getServerWorld().addScheduledTask(() -> {
                long now = player.world.getTotalWorldTime();
                Long last = lastSort.get(player.getUniqueID());
                if (last != null && now - last >= 0 && now - last < 4) return;
                lastSort.put(player.getUniqueID(), now);
                SortServer.sort(player, msg.windowId, msg.target, msg.ranks);
            });
            return null;
        }
    }

    public static class HelloHandler implements IMessageHandler<MsgHello, IMessage> {
        @Override
        public IMessage onMessage(MsgHello msg, MessageContext ctx) {
            proxy.onHello(msg);
            return null;
        }
    }
}
