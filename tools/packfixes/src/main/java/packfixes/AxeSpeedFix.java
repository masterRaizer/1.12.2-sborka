package packfixes;

import net.minecraft.block.material.Material;
import net.minecraft.init.Items;
import net.minecraft.item.Item;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.fml.common.eventhandler.EventPriority;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

/**
 * TreeChopper sets breakSpeed = original / (logs / 2) for whitelisted axes, so a wooden, stone or
 * iron axe on a big tree is slower than the bare hand. Runs after it and gives these three axes
 * their normal speed back; the whole tree still falls.
 */
public class AxeSpeedFix {

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onBreakSpeed(PlayerEvent.BreakSpeed event) {
        if (event.getNewSpeed() >= event.getOriginalSpeed()) return;
        Item held = event.getEntityPlayer().getHeldItemMainhand().getItem();
        if (held != Items.WOODEN_AXE && held != Items.STONE_AXE && held != Items.IRON_AXE) return;
        if (event.getState().getMaterial() != Material.WOOD) return;
        event.setNewSpeed(event.getOriginalSpeed());
    }
}
