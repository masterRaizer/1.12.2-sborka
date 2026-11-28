package chestsort;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

/** Client -> server: sort a slot group of the open container; ranks = order key per slot of the group. */
public class MsgSort implements IMessage {
    public static final int TARGET_CONTAINER = 0;
    public static final int TARGET_PLAYER = 1;

    public int windowId;
    public int target;
    public int[] ranks = new int[0];
    public boolean valid;

    public MsgSort() {
    }

    public MsgSort(int windowId, int target, int[] ranks) {
        this.windowId = windowId;
        this.target = target;
        this.ranks = ranks;
        this.valid = true;
    }

    @Override
    public void fromBytes(ByteBuf buf) {
        windowId = buf.readInt();
        target = buf.readByte();
        int n = buf.readShort();
        if (n < 0 || n > SortGroups.MAX_SLOTS || buf.readableBytes() < n * 4) {
            valid = false;
            return;
        }
        ranks = new int[n];
        for (int i = 0; i < n; i++) ranks[i] = buf.readInt();
        valid = target == TARGET_CONTAINER || target == TARGET_PLAYER;
    }

    @Override
    public void toBytes(ByteBuf buf) {
        buf.writeInt(windowId);
        buf.writeByte(target);
        buf.writeShort(ranks.length);
        for (int r : ranks) buf.writeInt(r);
    }
}
