package chestsort.client;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.util.ResourceLocation;
import net.minecraft.util.text.TextFormatting;
import net.minecraftforge.items.ItemHandlerHelper;

/** Sort criteria. Computed on the client (names in the player's language, creative tabs are client-only). */
public enum Criterion {
    NAME("name", "A"),
    MOD("mod", "M"),
    COUNT("count", "#"),
    CATEGORY("category", "C");

    public final String key;
    public final String letter;

    Criterion(String key, String letter) {
        this.key = key;
        this.letter = letter;
    }

    public static Criterion of(String key) {
        for (Criterion c : values()) if (c.key.equalsIgnoreCase(key)) return c;
        return NAME;
    }

    public Criterion next(boolean back) {
        Criterion[] v = values();
        return v[(ordinal() + (back ? v.length - 1 : 1)) % v.length];
    }

    private static final class Entry {
        final int slot;
        final ItemStack stack;
        final String name;
        final String mod;
        final int itemId;
        final int meta;
        final int tab;
        long total;

        Entry(int slot, ItemStack s) {
            this.slot = slot;
            this.stack = s;
            String n;
            try {
                n = TextFormatting.getTextWithoutFormattingCodes(s.getDisplayName());
            } catch (Throwable t) {
                n = null;
            }
            this.name = n == null ? "" : n.toLowerCase(Locale.ROOT);
            ResourceLocation rl = s.getItem().getRegistryName();
            this.mod = rl == null ? "~" : rl.getNamespace();
            this.itemId = Item.getIdFromItem(s.getItem());
            this.meta = s.getMetadata();
            int t;
            try {
                CreativeTabs ct = s.getItem().getCreativeTab();
                t = ct == null ? Integer.MAX_VALUE : ct.getIndex();
            } catch (Throwable e) {
                t = Integer.MAX_VALUE;
            }
            this.tab = t;
        }
    }

    private static final Comparator<Entry> BY_NAME = Comparator.<Entry, String>comparing(e -> e.name)
            .thenComparingInt(e -> e.itemId).thenComparingInt(e -> e.meta);

    private Comparator<Entry> comparator() {
        switch (this) {
            case MOD:
                return Comparator.<Entry>comparingInt(e -> "minecraft".equals(e.mod) ? 0 : 1)
                        .thenComparing(e -> e.mod).thenComparing(BY_NAME);
            case COUNT:
                return Comparator.<Entry>comparingLong(e -> -e.total).thenComparing(BY_NAME);
            case CATEGORY:
                return Comparator.<Entry>comparingInt(e -> e.tab).thenComparingInt(e -> e.itemId)
                        .thenComparingInt(e -> e.meta).thenComparing(e -> e.name);
            default:
                return BY_NAME;
        }
    }

    /** Order key for every slot of the group; empty slots get Integer.MAX_VALUE. */
    public int[] ranks(List<ItemStack> stacks) {
        int[] r = new int[stacks.size()];
        List<Entry> list = new ArrayList<>();
        for (int i = 0; i < r.length; i++) {
            r[i] = Integer.MAX_VALUE;
            ItemStack s = stacks.get(i);
            if (!s.isEmpty()) list.add(new Entry(i, s));
        }
        if (this == COUNT) {
            for (Entry a : list) {
                for (Entry b : list) {
                    if (ItemHandlerHelper.canItemStacksStack(a.stack, b.stack)) a.total += b.stack.getCount();
                }
            }
        }
        list.sort(comparator());
        for (int k = 0; k < list.size(); k++) r[list.get(k).slot] = k;
        return r;
    }
}
