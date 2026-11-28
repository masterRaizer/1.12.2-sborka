package chestsort;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

/** Server -> client: "this server sorts", plus the server's settings that decide slot groups. */
public class MsgHello implements IMessage {
    public boolean sortHotbar;
    public int minSlots;

    public MsgHello() {
    }

    public MsgHello(boolean sortHotbar, int minSlots) {
        this.sortHotbar = sortHotbar;
        this.minSlots = minSlots;
    }

    @Override
    public void fromBytes(ByteBuf buf) {
        sortHotbar = buf.readBoolean();
        minSlots = buf.readInt();
    }

    @Override
    public void toBytes(ByteBuf buf) {
        buf.writeBoolean(sortHotbar);
        buf.writeInt(minSlots);
    }
}
