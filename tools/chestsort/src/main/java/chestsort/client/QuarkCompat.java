package chestsort.client;

import java.lang.reflect.Field;

import net.minecraft.client.gui.GuiTextField;

/** Quark's chest search bar sits in the chest's title row, where our buttons are: shorten it so both fit. */
final class QuarkCompat {
    private static boolean looked;
    private static Field field;

    private QuarkCompat() {
    }

    private static GuiTextField searchBar() {
        if (!looked) {
            looked = true;
            try {
                field = Class.forName("vazkii.quark.client.feature.ChestSearchBar").getField("searchBar");
            } catch (Throwable t) {
                field = null;
            }
        }
        if (field == null) return null;
        try {
            Object o = field.get(null);
            return o instanceof GuiTextField ? (GuiTextField) o : null;
        } catch (Throwable t) {
            return null;
        }
    }

    /** Make the search bar end left of the area [left, right) x [top, bottom) if it overlaps it. */
    static void keepClear(int left, int top, int right, int bottom) {
        GuiTextField sb = searchBar();
        if (sb == null) return;
        if (sb.x >= right || sb.x + sb.width <= left || sb.y >= bottom || sb.y + sb.height <= top) return;
        int w = left - 2 - sb.x;
        if (w >= 20) sb.width = w;
    }
}
