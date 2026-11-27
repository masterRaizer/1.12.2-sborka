package lakmoore.sel.client;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import net.minecraft.block.Block;
import net.minecraft.block.state.IBlockState;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;

/**
 * Added to Smooth Entity Light 4.0.4 by PatchSel: an item that is not in "Light Items"
 * glows with the light value of its block (torch 14, glowstone 15, ...).
 * Only for Config.itemsMap; floodlight and water lists keep the original behaviour.
 */
public final class SELAutoLight {
    private static final Map<Item, Map<Integer, Integer>> CACHE = new ConcurrentHashMap<Item, Map<Integer, Integer>>();

    private SELAutoLight() {}

    public static int get(ItemConfigHelper helper, ItemStack stack) {
        if (stack == null) return 0;
        Item item = stack.func_77973_b();
        if (item == null) return 0;
        int meta = stack.func_77960_j();
        int v = helper.retrieveValue(item.getRegistryName(), meta);
        if (v >= 0) return v;
        if (helper != Config.itemsMap || !(item instanceof ItemBlock)) return 0;
        Map<Integer, Integer> m = CACHE.get(item);
        if (m == null) {
            m = new ConcurrentHashMap<Integer, Integer>();
            CACHE.put(item, m);
        }
        Integer c = m.get(meta);
        if (c == null) {
            c = compute((ItemBlock) item, meta);
            m.put(meta, c);
        }
        return c;
    }

    private static int compute(ItemBlock item, int meta) {
        try {
            Block b = item.func_179223_d();
            if (b == null) return 0;
            IBlockState st;
            try {
                st = b.func_176203_a(item.func_77647_b(meta));
            } catch (Throwable t) {
                st = b.func_176223_P();
            }
            int l = st.func_185906_d();
            return l < 0 ? 0 : (l > 15 ? 15 : l);
        } catch (Throwable t) {
            return 0;
        }
    }
}
