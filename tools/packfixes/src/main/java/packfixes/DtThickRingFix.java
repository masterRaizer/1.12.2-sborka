package packfixes;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.block.Block;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.IResource;
import net.minecraft.client.resources.IResourceManager;
import net.minecraft.util.ResourceLocation;
import net.minecraftforge.client.event.TextureStitchEvent;
import net.minecraftforge.fml.common.eventhandler.EventPriority;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.registry.ForgeRegistries;

import java.io.InputStreamReader;
import java.io.Reader;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * Dynamic Trees adds the generated "<log_top>_thick" ring sprite of a 3x3 trunk to its texture list only from the
 * ModelBlockBranchThick constructor. VintageFix dynamic_resources builds models lazily, after the atlas is stitched,
 * so most rings never get into the atlas and the trunk's top/bottom face renders as the missing texture.
 * Here we read each thick branch's model JSON ourselves and hand the ring location to Dynamic Trees before its own
 * stitch handler (NORMAL priority) runs. Reflection only: no compile dependency on Dynamic Trees.
 */
public class DtThickRingFix {

    private static final String THICK_BLOCK = "com.ferreusveritas.dynamictrees.blocks.BlockBranchThick";
    private static final String HANDLER = "com.ferreusveritas.dynamictrees.event.TextureGenerationHandler";

    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onStitch(TextureStitchEvent.Pre event) {
        if (event.getMap() != Minecraft.getMinecraft().getTextureMapBlocks()) return;
        Class<?> thick;
        Method add;
        try {
            thick = Class.forName(THICK_BLOCK);
            add = Class.forName(HANDLER).getMethod("addRingTextureLocation", ResourceLocation.class);
        } catch (Throwable t) {
            PackFixes.LOG.warn("Dynamic Trees classes not found, thick ring fix skipped: {}", t.toString());
            return;
        }
        IResourceManager rm = Minecraft.getMinecraft().getResourceManager();
        int ok = 0;
        for (Block block : ForgeRegistries.BLOCKS) {
            if (!thick.isInstance(block) || block.getRegistryName() == null) continue;
            ResourceLocation id = block.getRegistryName();
            try {
                ResourceLocation model = findModel(rm, id);
                String rings = model == null ? null : findRings(rm, model, 0);
                if (rings == null) {
                    PackFixes.LOG.warn("No rings texture for thick branch {}", id);
                    continue;
                }
                add.invoke(null, new ResourceLocation(rings));
                ok++;
            } catch (Throwable t) {
                PackFixes.LOG.warn("Thick ring fix failed for {}: {}", id, t.toString());
            }
        }
        PackFixes.LOG.info("Registered ring textures for {} Dynamic Trees thick branches", ok);
    }

    /** blockstates/<id>.json -> first variant model "ns:name#dynamicthick" -> models/block/name.json */
    private static ResourceLocation findModel(IResourceManager rm, ResourceLocation id) {
        JsonObject bs = readJson(rm, new ResourceLocation(id.getNamespace(), "blockstates/" + id.getPath() + ".json"));
        if (bs != null && bs.has("variants")) {
            for (Map.Entry<String, JsonElement> e : bs.getAsJsonObject("variants").entrySet()) {
                JsonElement v = e.getValue();
                if (v.isJsonArray() && v.getAsJsonArray().size() > 0) v = v.getAsJsonArray().get(0);
                if (v.isJsonObject() && v.getAsJsonObject().has("model")) {
                    String m = v.getAsJsonObject().get("model").getAsString();
                    int hash = m.indexOf('#');
                    if (hash >= 0) m = m.substring(0, hash);
                    ResourceLocation ml = new ResourceLocation(m.contains(":") ? m : id.getNamespace() + ":" + m);
                    return new ResourceLocation(ml.getNamespace(), "models/block/" + ml.getPath() + ".json");
                }
            }
        }
        String path = id.getPath();
        if (path.endsWith("x")) path = path.substring(0, path.length() - 1);
        return new ResourceLocation(id.getNamespace(), "models/block/" + path + ".json");
    }

    /** textures.rings of the model, following "parent" a few levels if needed. */
    private static String findRings(IResourceManager rm, ResourceLocation model, int depth) {
        if (depth > 5) return null;
        JsonObject json = readJson(rm, model);
        if (json == null) return null;
        if (json.has("textures") && json.getAsJsonObject("textures").has("rings")) {
            String r = json.getAsJsonObject("textures").get("rings").getAsString();
            if (!r.startsWith("#")) return r;
        }
        if (json.has("parent")) {
            ResourceLocation p = new ResourceLocation(json.get("parent").getAsString());
            return findRings(rm, new ResourceLocation(p.getNamespace(), "models/" + p.getPath() + ".json"), depth + 1);
        }
        return null;
    }

    private static JsonObject readJson(IResourceManager rm, ResourceLocation loc) {
        try (IResource res = rm.getResource(loc);
             Reader r = new InputStreamReader(res.getInputStream(), StandardCharsets.UTF_8)) {
            JsonElement el = new JsonParser().parse(r);
            return el.isJsonObject() ? el.getAsJsonObject() : null;
        } catch (Exception e) {
            return null;
        }
    }
}
