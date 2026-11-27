package dynlight;

import net.minecraft.util.math.BlockPos;

/**
 * Current dynamic light sources as one immutable array {x, y, z, luminance, x, y, z, luminance, ...}.
 * Written once per client tick, read from the render thread and the chunk builder threads, so it is a volatile
 * reference to an array that is never changed after publishing. The read path allocates nothing.
 */
public final class LightSources {

    public static final double[] EMPTY = new double[0];
    public static volatile double[] snapshot = EMPTY;

    private LightSources() {
    }

    /**
     * Adds the dynamic block light at {@code pos} to a packed light value (sky << 20 | block << 4).
     * The block part becomes max(stored, dynamic); the sky part is never touched.
     */
    public static int apply(int packed, BlockPos pos) {
        final double[] s = snapshot;
        final int n = s.length;
        if (n == 0 || pos == null) {
            return packed;
        }
        final double px = pos.getX() + 0.5D;
        final double py = pos.getY() + 0.5D;
        final double pz = pos.getZ() + 0.5D;
        double best = 0.0D;
        for (int i = 0; i < n; i += 4) {
            final double lum = s[i + 3];
            if (lum <= best) {
                continue;
            }
            final double dx = px - s[i];
            final double dy = py - s[i + 1];
            final double dz = pz - s[i + 2];
            final double d2 = dx * dx + dy * dy + dz * dz;
            if (d2 >= lum * lum) {
                continue;
            }
            final double v = lum - Math.sqrt(d2);
            if (v > best) {
                best = v;
            }
        }
        if (best <= 0.0D) {
            return packed;
        }
        int dyn = (int) (best * 16.0D);
        if (dyn > 240) {
            dyn = 240;
        }
        final int block = packed & 0xFFFF;
        if (dyn <= block) {
            return packed;
        }
        return (packed & 0xFFFF0000) | dyn;
    }
}
