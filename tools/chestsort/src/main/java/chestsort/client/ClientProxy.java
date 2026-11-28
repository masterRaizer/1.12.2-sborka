package chestsort.client;

import chestsort.CommonProxy;
import chestsort.MsgHello;
import net.minecraft.client.Minecraft;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.network.FMLNetworkEvent;

public class ClientProxy extends CommonProxy {
    /** Set when the server says it has the mod; buttons appear only then. */
    public static volatile boolean serverReady;
    public static volatile boolean sortHotbar;
    public static volatile int minSlots = 18;

    @Override
    public void init() {
        MinecraftForge.EVENT_BUS.register(new ClientEvents());
        MinecraftForge.EVENT_BUS.register(this);
    }

    @Override
    public void onHello(MsgHello msg) {
        Minecraft.getMinecraft().addScheduledTask(() -> {
            sortHotbar = msg.sortHotbar;
            minSlots = msg.minSlots;
            serverReady = true;
        });
    }

    @SubscribeEvent
    public void onDisconnect(FMLNetworkEvent.ClientDisconnectionFromServerEvent e) {
        serverReady = false;
    }
}
