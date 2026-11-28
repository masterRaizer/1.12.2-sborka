package chestsort.client;

import java.util.ArrayList;
import java.util.List;

import chestsort.ChestSort;
import chestsort.MsgSort;
import chestsort.SortConfig;
import chestsort.SortGroups;
import net.minecraft.client.Minecraft;
import net.minecraft.client.audio.PositionedSoundRecord;
import net.minecraft.client.gui.GuiButton;
import net.minecraft.client.gui.GuiScreen;
import net.minecraft.client.gui.inventory.GuiContainer;
import net.minecraft.client.gui.inventory.GuiContainerCreative;
import net.minecraft.client.resources.I18n;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.init.SoundEvents;
import net.minecraft.inventory.Container;
import net.minecraft.item.ItemStack;
import net.minecraftforge.client.event.GuiScreenEvent;
import net.minecraftforge.fml.common.eventhandler.EventPriority;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;

public class ClientEvents {
    public static final int ID_CONTAINER_SORT = 7701;
    public static final int ID_CONTAINER_CRIT = 7702;
    public static final int ID_PLAYER_SORT = 7703;
    public static final int ID_PLAYER_CRIT = 7704;
    private static final long LABEL_MS = 2500;

    private static Criterion current;
    private final List<SortButton> buttons = new ArrayList<>();
    private SortButton labelButton;
    private long labelUntil;

    static Criterion criterion() {
        if (current == null) current = Criterion.of(SortConfig.criterion);
        return current;
    }

    @SubscribeEvent(priority = EventPriority.LOW) // after Quark builds its search bar
    public void onInit(GuiScreenEvent.InitGuiEvent.Post e) {
        buttons.clear();
        labelButton = null;
        GuiScreen screen = e.getGui();
        if (!(screen instanceof GuiContainer) || screen instanceof GuiContainerCreative) return;
        if (!ClientProxy.serverReady || SortConfig.blacklistGuis.contains(screen.getClass().getName())) return;
        GuiContainer gui = (GuiContainer) screen;
        EntityPlayer p = Minecraft.getMinecraft().player;
        if (p == null) return;
        Container c = gui.inventorySlots;
        if (SortConfig.containerButtons) {
            int[] g = SortGroups.containerGroup(c, p, ClientProxy.minSlots);
            if (g != null) add(e, gui, MsgSort.TARGET_CONTAINER, g, ID_CONTAINER_SORT, ID_CONTAINER_CRIT);
        }
        if (SortConfig.playerButtons) {
            int[] g = SortGroups.playerGroup(c, p, ClientProxy.sortHotbar);
            if (g != null) add(e, gui, MsgSort.TARGET_PLAYER, g, ID_PLAYER_SORT, ID_PLAYER_CRIT);
        }
        clearQuark(gui);
    }

    private void add(GuiScreenEvent.InitGuiEvent.Post e, GuiContainer gui, int target, int[] g, int sortId, int critId) {
        SortButton sort = new SortButton(sortId, gui, target, false, g);
        SortButton crit = new SortButton(critId, gui, target, true, g);
        e.getButtonList().add(sort);
        e.getButtonList().add(crit);
        buttons.add(sort);
        buttons.add(crit);
    }

    @SubscribeEvent
    public void onAction(GuiScreenEvent.ActionPerformedEvent.Pre e) {
        GuiButton b = e.getButton();
        if (!(b instanceof SortButton) || !buttons.contains(b)) return;
        e.setCanceled(true);
        SortButton sb = (SortButton) b;
        Minecraft mc = Minecraft.getMinecraft();
        mc.getSoundHandler().playSound(PositionedSoundRecord.getMasterRecord(SoundEvents.UI_BUTTON_CLICK, 1.0F));
        if (sb.criterionButton) {
            current = criterion().next(GuiScreen.isShiftKeyDown());
            SortConfig.saveCriterion(current.key);
        } else {
            sendSort(mc, sb);
        }
        labelButton = sb;
        labelUntil = System.currentTimeMillis() + LABEL_MS;
    }

    private static void sendSort(Minecraft mc, SortButton sb) {
        EntityPlayer p = mc.player;
        if (p == null || !p.inventory.getItemStack().isEmpty()) return;
        Container c = sb.gui.inventorySlots;
        int[] g = sb.isPlayer() ? SortGroups.playerGroup(c, p, ClientProxy.sortHotbar)
                : SortGroups.containerGroup(c, p, ClientProxy.minSlots);
        if (g == null) return;
        List<ItemStack> stacks = new ArrayList<>(g.length);
        for (int i : g) stacks.add(c.getSlot(i).getStack());
        ChestSort.net.sendToServer(new MsgSort(c.windowId, sb.target, criterion().ranks(stacks)));
    }

    @SubscribeEvent
    public void onDrawPre(GuiScreenEvent.DrawScreenEvent.Pre e) {
        clearQuark(e.getGui());
    }

    private void clearQuark(GuiScreen screen) {
        int left = Integer.MAX_VALUE, top = Integer.MAX_VALUE, right = Integer.MIN_VALUE, bottom = Integer.MIN_VALUE;
        for (SortButton b : buttons) {
            if (b.gui != screen || b.isPlayer()) continue;
            b.place();
            if (!b.visible) continue;
            left = Math.min(left, b.x);
            top = Math.min(top, b.y);
            right = Math.max(right, b.x + b.width);
            bottom = Math.max(bottom, b.y + b.height);
        }
        if (left < right) QuarkCompat.keepClear(left, top, right, bottom);
    }

    @SubscribeEvent
    public void onDraw(GuiScreenEvent.DrawScreenEvent.Post e) {
        if (buttons.isEmpty() || !(e.getGui() instanceof GuiContainer)) return;
        GuiContainer gui = (GuiContainer) e.getGui();
        int mx = e.getMouseX(), my = e.getMouseY();
        SortButton shown = null;
        for (SortButton b : buttons) {
            if (b.gui == gui && b.visible && b.isMouseOver()) shown = b;
        }
        boolean label = false;
        if (shown == null && labelButton != null && labelButton.gui == gui && System.currentTimeMillis() < labelUntil) {
            shown = labelButton;
            label = true;
        }
        if (shown == null) return;
        String crit = I18n.format("chestsort.crit." + criterion().key);
        List<String> lines = new ArrayList<>();
        if (label) {
            lines.add(I18n.format("chestsort.sorted", crit));
        } else if (shown.criterionButton) {
            lines.add(I18n.format("chestsort.criterion", crit));
            lines.add("§7" + I18n.format("chestsort.hint"));
        } else {
            lines.add(I18n.format("chestsort.sort", crit));
            if (shown.isPlayer() && !ClientProxy.sortHotbar) lines.add("§7" + I18n.format("chestsort.hotbar"));
        }
        int x = label ? shown.x : mx;
        int y = label ? shown.y : my;
        gui.drawHoveringText(lines, x, y);
    }
}
