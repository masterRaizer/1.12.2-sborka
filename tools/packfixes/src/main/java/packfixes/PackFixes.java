package packfixes;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.config.Configuration;
import net.minecraftforge.fml.common.Loader;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Small fixes for the 1.12.2 pack. Every fix can be turned off in config/packfixes.cfg.
 * Works on client and server; either side may run without it.
 */
@Mod(modid = "packfixes", name = "Pack Fixes", version = "0.2.0",
        acceptableRemoteVersions = "*", acceptedMinecraftVersions = "[1.12.2]")
public class PackFixes {

    static final Logger LOG = LogManager.getLogger("packfixes");

    @Mod.EventHandler
    public void preInit(FMLPreInitializationEvent event) {
        Configuration cfg = new Configuration(event.getSuggestedConfigurationFile());
        boolean dtRings = cfg.getBoolean("dynamicTreesThickRings", "fixes", true,
                "Client: register Dynamic Trees thick-trunk ring textures before the block atlas is stitched. "
                        + "Without it, with VintageFix dynamic_resources the top/bottom of 3x3 trunks is purple-black.");
        boolean axes = cfg.getBoolean("vanillaAxesFullSpeed", "fixes", true,
                "Client and server: wooden, stone and iron axes keep their normal chopping speed while "
                        + "TreeChopper fells the whole tree (TreeChopper divides the speed by half the log count). "
                        + "Must match on client and server.");
        if (cfg.hasChanged()) cfg.save();

        if (dtRings && event.getSide().isClient() && Loader.isModLoaded("dynamictrees")) {
            try {
                // by name, so the server never loads client-only classes
                Object fix = Class.forName("packfixes.DtThickRingFix").newInstance();
                MinecraftForge.EVENT_BUS.register(fix);
                LOG.info("Dynamic Trees thick ring fix enabled");
            } catch (Throwable t) {
                LOG.error("Dynamic Trees thick ring fix failed to start", t);
            }
        }
        if (axes && Loader.isModLoaded("treechopper")) {
            MinecraftForge.EVENT_BUS.register(new AxeSpeedFix());
            LOG.info("Vanilla axe speed fix enabled");
        }
    }
}
