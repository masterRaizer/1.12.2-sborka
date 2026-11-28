package chestsort;

import java.io.File;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import net.minecraftforge.common.config.Configuration;

public final class SortConfig {
    private static final String GENERAL = "general";
    private static final String CLIENT = "client";

    public static Configuration cfg;

    public static boolean serverEnabled = true;
    public static boolean sortHotbar = false;
    public static int minContainerSlots = 18;
    public static Set<String> extraSlotClasses = new HashSet<>();
    public static Set<String> blacklistContainers = new HashSet<>();

    public static boolean containerButtons = true;
    public static boolean playerButtons = true;
    public static Set<String> blacklistGuis = new HashSet<>();
    public static String criterion = "name";

    private SortConfig() {
    }

    static void load(File file) {
        cfg = new Configuration(file);
        serverEnabled = cfg.getBoolean("serverEnabled", GENERAL, true,
                "Server side: perform sorting. false = sort requests are ignored and clients get no buttons.");
        sortHotbar = cfg.getBoolean("sortHotbar", GENERAL, false,
                "Server side: also sort the hotbar (bottom 9 slots) when sorting the player inventory.");
        minContainerSlots = cfg.getInt("minContainerSlots", GENERAL, 18, 9, SortGroups.MAX_SLOTS,
                "Server side: a container needs at least this many storage slots to get a sort button (keeps machines out).");
        extraSlotClasses = set(cfg.getStringList("extraSlotClasses", GENERAL, new String[0],
                "Extra slot class names (full) treated as plain storage slots. By default only vanilla Slot, SlotItemHandler and SlotShulkerBox."));
        blacklistContainers = set(cfg.getStringList("blacklistContainers", GENERAL, new String[0],
                "Container class names (full) that are never sorted."));
        containerButtons = cfg.getBoolean("containerButtons", CLIENT, true, "Client: show the sort buttons for chests and other containers.");
        playerButtons = cfg.getBoolean("playerButtons", CLIENT, true, "Client: show the sort buttons for the player inventory.");
        blacklistGuis = set(cfg.getStringList("blacklistGuis", CLIENT, new String[0],
                "Client: GUI class names (full) where no buttons are shown."));
        criterion = cfg.getString("criterion", CLIENT, "name", "Client: current sort criterion (switched with the small button).",
                new String[]{"name", "mod", "count", "category"});
        if (cfg.hasChanged()) cfg.save();
    }

    public static void saveCriterion(String value) {
        criterion = value;
        cfg.get(CLIENT, "criterion", "name").set(value);
        cfg.save();
    }

    private static Set<String> set(String[] arr) {
        Set<String> s = new HashSet<>();
        for (String x : arr) {
            String t = x.trim();
            if (!t.isEmpty()) s.add(t);
        }
        return s;
    }

    static Set<String> of(String... a) {
        return new HashSet<>(Arrays.asList(a));
    }
}
