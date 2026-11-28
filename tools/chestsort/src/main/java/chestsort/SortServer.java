package chestsort;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.inventory.Container;
import net.minecraft.inventory.Slot;
import net.minecraft.item.ItemStack;
import net.minecraftforge.items.ItemHandlerHelper;

/** Server-side sort: merge equal stacks, order them by the client's keys, put them back. Never changes totals. */
public final class SortServer {
    private SortServer() {
    }

    private static final class Kind {
        final ItemStack proto;
        long count;
        int rank;
        final int first;

        Kind(ItemStack proto, int rank, int first) {
            this.proto = proto;
            this.rank = rank;
            this.first = first;
        }
    }

    /** @return true if the inventory was rearranged */
    public static boolean sort(EntityPlayerMP p, int windowId, int target, int[] ranks) {
        Container c = p.openContainer;
        if (c == null || c.windowId != windowId) return false;
        if (!p.inventory.getItemStack().isEmpty()) return false;
        if (SortConfig.blacklistContainers.contains(c.getClass().getName())) return false;
        if (c != p.inventoryContainer && !c.canInteractWith(p)) return false;
        int[] idx = target == MsgSort.TARGET_PLAYER
                ? SortGroups.playerGroup(c, p, SortConfig.sortHotbar)
                : SortGroups.containerGroup(c, p, SortConfig.minContainerSlots);
        if (idx == null || idx.length != ranks.length) return false;

        List<Kind> kinds = new ArrayList<>();
        long total = 0;
        for (int i = 0; i < idx.length; i++) {
            Slot s = c.getSlot(idx[i]);
            ItemStack st = s.getStack();
            if (st.isEmpty()) continue;
            if (!s.canTakeStack(p)) return false;
            total += st.getCount();
            Kind k = null;
            for (Kind x : kinds) {
                if (ItemHandlerHelper.canItemStacksStack(x.proto, st)) {
                    k = x;
                    break;
                }
            }
            if (k == null) {
                k = new Kind(st.copy(), ranks[i], i);
                kinds.add(k);
            } else if (ranks[i] < k.rank) {
                k.rank = ranks[i];
            }
            k.count += st.getCount();
        }
        if (kinds.isEmpty()) return false;
        kinds.sort((a, b) -> a.rank != b.rank ? Integer.compare(a.rank, b.rank) : Integer.compare(a.first, b.first));

        ItemStack[] out = new ItemStack[idx.length];
        int pos = 0;
        long placed = 0;
        for (Kind k : kinds) {
            long left = k.count;
            while (left > 0) {
                if (pos >= idx.length) return false;
                Slot s = c.getSlot(idx[pos]);
                ItemStack piece = k.proto.copy();
                int max = Math.min(piece.getMaxStackSize(), s.getItemStackLimit(piece));
                if (max <= 0) return false;
                int amount = (int) Math.min(max, left);
                piece.setCount(amount);
                if (!s.isItemValid(piece)) return false;
                out[pos++] = piece;
                left -= amount;
                placed += amount;
            }
        }
        if (placed != total) return false;
        for (int i = pos; i < out.length; i++) out[i] = ItemStack.EMPTY;

        boolean changed = false;
        for (int i = 0; i < idx.length; i++) {
            Slot s = c.getSlot(idx[i]);
            if (!ItemStack.areItemStacksEqual(s.getStack(), out[i])) {
                s.putStack(out[i]);
                changed = true;
            }
        }
        if (changed) c.detectAndSendChanges();
        return changed;
    }
}
