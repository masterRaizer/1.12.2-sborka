package chestsort.client;

import chestsort.MsgSort;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Gui;
import net.minecraft.client.gui.GuiButton;
import net.minecraft.client.gui.inventory.GuiContainer;
import net.minecraft.client.renderer.GlStateManager;
import net.minecraft.inventory.Slot;

/** 9x9 button placed in the label row above a slot group, at its right edge. Position follows the GUI each frame. */
public class SortButton extends GuiButton {
    public static final int SIZE = 9;

    final GuiContainer gui;
    final int target;
    final boolean criterionButton;
    final int[] slots;

    public SortButton(int id, GuiContainer gui, int target, boolean criterionButton, int[] slots) {
        super(id, 0, 0, SIZE, SIZE, "");
        this.gui = gui;
        this.target = target;
        this.criterionButton = criterionButton;
        this.slots = slots;
        place();
    }

    void place() {
        int maxX = Integer.MIN_VALUE, minY = Integer.MAX_VALUE;
        for (int i : slots) {
            if (i >= gui.inventorySlots.inventorySlots.size()) continue;
            Slot s = gui.inventorySlots.getSlot(i);
            maxX = Math.max(maxX, s.xPos);
            minY = Math.min(minY, s.yPos);
        }
        if (maxX == Integer.MIN_VALUE) {
            visible = false;
            return;
        }
        x = gui.getGuiLeft() + maxX + 16 - SIZE - (criterionButton ? 0 : SIZE + 1);
        y = gui.getGuiTop() + minY - 11;
    }

    @Override
    public void drawButton(Minecraft mc, int mouseX, int mouseY, float partialTicks) {
        place();
        if (!visible) return;
        hovered = mouseX >= x && mouseY >= y && mouseX < x + width && mouseY < y + height;
        GlStateManager.disableLighting();
        GlStateManager.disableDepth();
        int border = hovered ? 0xFFFFFFFF : 0xFF373737;
        int fill = hovered ? 0xFF7F9FCF : 0xFF8B8B8B;
        Gui.drawRect(x, y, x + SIZE, y + SIZE, border);
        Gui.drawRect(x + 1, y + 1, x + SIZE - 1, y + SIZE - 1, fill);
        if (criterionButton) {
            String l = ClientEvents.criterion().letter;
            int w = mc.fontRenderer.getStringWidth(l);
            mc.fontRenderer.drawString(l, x + (SIZE - w) / 2 + 1, y + 1, 0xFFFFFF, false);
        } else {
            int c = 0xFF202020;
            Gui.drawRect(x + 2, y + 2, x + 7, y + 3, c);
            Gui.drawRect(x + 2, y + 4, x + 6, y + 5, c);
            Gui.drawRect(x + 2, y + 6, x + 5, y + 7, c);
        }
        GlStateManager.enableDepth();
    }

    boolean isPlayer() {
        return target == MsgSort.TARGET_PLAYER;
    }
}
