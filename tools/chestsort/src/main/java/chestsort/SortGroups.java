package chestsort;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;

import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.InventoryPlayer;
import net.minecraft.inventory.Container;
import net.minecraft.inventory.Slot;
import net.minecraft.inventory.SlotShulkerBox;
import net.minecraftforge.items.IItemHandlerModifiable;
import net.minecraftforge.items.SlotItemHandler;

/**
 * Finds the slot groups that may be sorted. Used on both sides with the same rules, so the client's list of
 * slots matches the server's (the server refuses when the lengths differ).
 */
public final class SortGroups {
    public static final int MAX_SLOTS = 512;

    private SortGroups() {
    }

    static boolean plainSlot(Slot s) {
        Class<?> c = s.getClass();
        return c == Slot.class || c == SlotItemHandler.class || c == SlotShulkerBox.class
                || SortConfig.extraSlotClasses.contains(c.getName());
    }

    /** Player main inventory (rows above the hotbar, or all 36 with hotbar). null if not cleanly present. */
    public static int[] playerGroup(Container c, EntityPlayer p, boolean withHotbar) {
        int from = withHotbar ? 0 : 9;
        List<Integer> out = new ArrayList<>();
        boolean[] seen = new boolean[36];
        for (int i = 0; i < c.inventorySlots.size(); i++) {
            Slot s = c.inventorySlots.get(i);
            if (s.inventory != p.inventory) continue;
            int idx = s.getSlotIndex();
            if (idx < from || idx >= 36) continue;
            if (!plainSlot(s) || seen[idx]) return null; // locked/special slot (e.g. a backpack being open) or duplicate
            seen[idx] = true;
            out.add(i);
        }
        if (out.size() != 36 - from) return null;
        return toArray(out);
    }

    /** The biggest non-player storage inventory of the container. null if there is none that is safe to sort. */
    public static int[] containerGroup(Container c, EntityPlayer p, int minSlots) {
        Map<Object, List<Integer>> groups = new IdentityHashMap<>();
        for (int i = 0; i < c.inventorySlots.size(); i++) {
            Slot s = c.inventorySlots.get(i);
            if (s.inventory instanceof InventoryPlayer) continue;
            Object key = s instanceof SlotItemHandler ? ((SlotItemHandler) s).getItemHandler() : s.inventory;
            groups.computeIfAbsent(key, k -> new ArrayList<>()).add(i);
        }
        List<Integer> best = null;
        for (List<Integer> g : groups.values()) {
            if (best == null || g.size() > best.size()) best = g;
        }
        if (best == null || best.size() < minSlots || best.size() > MAX_SLOTS) return null;
        for (int i : best) {
            Slot s = c.inventorySlots.get(i);
            if (!plainSlot(s) || s.getSlotStackLimit() != 64) return null;
            if (s instanceof SlotItemHandler && !(((SlotItemHandler) s).getItemHandler() instanceof IItemHandlerModifiable)) return null;
        }
        return toArray(best);
    }

    private static int[] toArray(List<Integer> l) {
        int[] a = new int[l.size()];
        for (int i = 0; i < a.length; i++) a[i] = l.get(i);
        return a;
    }
}
