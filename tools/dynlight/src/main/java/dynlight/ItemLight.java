package dynlight;

import net.minecraft.block.Block;
import net.minecraft.block.state.IBlockState;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraft.util.ResourceLocation;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.FluidUtil;
import org.apache.logging.log4j.Logger;

import java.util.HashMap;
import java.util.Map;

/** Brightness of an item: config override, else the light value of its block, else the fluid inside it. */
final class ItemLight {

    private static final Map<Long, Integer> CACHE = new HashMap<>();
    private static final Map<String, Integer> OVERRIDES = new HashMap<>();

    private ItemLight() {
    }

    static void reload(String[] overrides, Logger log) {
        CACHE.clear();
        OVERRIDES.clear();
        if (overrides == null) {
            return;
        }
        for (String line : overrides) {
            if (line == null) {
                continue;
            }
            int eq = line.lastIndexOf('=');
            if (eq <= 0) {
                continue;
            }
            try {
                int v = Integer.parseInt(line.substring(eq + 1).trim());
                OVERRIDES.put(line.substring(0, eq).trim(), Math.max(0, Math.min(15, v)));
            } catch (NumberFormatException e) {
                log.warn("Bad item light line '{}', skipped", line);
            }
        }
    }

    static int of(ItemStack stack, boolean checkFluids) {
        if (stack == null || stack.isEmpty()) {
            return 0;
        }
        Item item = stack.getItem();
        int meta = stack.getMetadata();
        Long key = ((long) Item.getIdFromItem(item) << 16) | (meta & 0xFFFFL);
        Integer cached = CACHE.get(key);
        int v;
        if (cached != null) {
            v = cached;
        } else {
            v = compute(item, meta);
            CACHE.put(key, v);
        }
        if (v == 0 && checkFluids && !hasOverride(item, meta)) {
            v = fluidLight(stack);
        }
        return v;
    }

    private static boolean hasOverride(Item item, int meta) {
        ResourceLocation rl = item.getRegistryName();
        return rl != null && (OVERRIDES.containsKey(rl + "@" + meta) || OVERRIDES.containsKey(rl.toString()));
    }

    private static int compute(Item item, int meta) {
        ResourceLocation rl = item.getRegistryName();
        if (rl != null) {
            Integer o = OVERRIDES.get(rl + "@" + meta);
            if (o == null) {
                o = OVERRIDES.get(rl.toString());
            }
            if (o != null) {
                return o;
            }
        }
        if (item instanceof ItemBlock) {
            try {
                Block block = ((ItemBlock) item).getBlock();
                @SuppressWarnings("deprecation")
                IBlockState state = block.getStateFromMeta(item.getMetadata(meta));
                @SuppressWarnings("deprecation")
                int light = state.getLightValue();
                return Math.max(0, Math.min(15, light));
            } catch (Throwable t) {
                return 0;
            }
        }
        return 0;
    }

    private static int fluidLight(ItemStack stack) {
        try {
            FluidStack fs = FluidUtil.getFluidContained(stack);
            if (fs != null && fs.getFluid() != null && fs.amount > 0) {
                return Math.max(0, Math.min(15, fs.getFluid().getLuminosity(fs)));
            }
        } catch (Throwable ignored) {
            // a broken fluid capability of some mod must not stop the light
        }
        return 0;
    }
}
