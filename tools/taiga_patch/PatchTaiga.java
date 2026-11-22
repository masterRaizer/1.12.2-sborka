import org.objectweb.asm.*;

import java.io.*;
import java.util.*;
import java.util.zip.*;

/**
 * TAIGA 1.3.4: fixes cascading worldgen.
 *
 * com/sosnitzka/taiga/util/Generator places single blocks, cubes and meteors at chunkX*16 + nextInt(16)
 * without vanilla's +8 offset, so setBlockState/neighbour updates at the chunk edge load the not yet generated
 * neighbour chunk. This patch adds "x += 8; z += 8" at the start of the affected methods, which moves all
 * placements into the populated 2x2 chunk area like vanilla does. generateOre(...) that uses TAIGA's
 * WorldGenMinable is NOT touched: that class already adds +8 itself.
 *
 * Usage (Java 8): javac -cp asm-debug-all-5.2.jar PatchTaiga.java
 *                 java -cp asm-debug-all-5.2.jar;. PatchTaiga <in.jar> <out.jar>
 */
public class PatchTaiga {
    static final String CLS = "com/sosnitzka/taiga/util/Generator.class";
    // method name -> {x local, z local}
    static final Map<String, int[]> TARGETS = new HashMap<>();
    static {
        TARGETS.put("generateOreDescending", new int[]{3, 4});
        TARGETS.put("generateOreStoneVariant", new int[]{3, 4});
        TARGETS.put("generateOreBottom", new int[]{3, 4});
        TARGETS.put("generateMeteor", new int[]{3, 4});
        TARGETS.put("generateCube", new int[]{4, 5});
    }

    public static void main(String[] a) throws Exception {
        Set<String> patched = new TreeSet<>();
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(a[0]));
             ZipOutputStream out = new ZipOutputStream(new FileOutputStream(a[1]))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                byte[] data = readAll(in);
                if (e.getName().equals(CLS)) data = patch(data, patched);
                out.putNextEntry(new ZipEntry(e.getName()));
                out.write(data);
                out.closeEntry();
            }
        }
        if (patched.size() != TARGETS.size()) {
            new File(a[1]).delete();
            throw new IllegalStateException("patched " + patched + ", expected " + TARGETS.keySet());
        }
        System.out.println("patched: " + patched);
    }

    static byte[] patch(byte[] cls, Set<String> patched) {
        ClassReader cr = new ClassReader(cls);
        ClassWriter cw = new ClassWriter(cr, 0);
        cr.accept(new ClassVisitor(Opcodes.ASM5, cw) {
            @Override
            public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] ex) {
                MethodVisitor mv = super.visitMethod(acc, name, desc, sig, ex);
                final int[] xz = TARGETS.get(name);
                if (xz == null) return mv;
                Type[] args = Type.getArgumentTypes(desc);
                if ((acc & Opcodes.ACC_STATIC) == 0 || args.length <= xz[1]
                        || args[xz[0]] != Type.INT_TYPE || args[xz[1]] != Type.INT_TYPE)
                    throw new IllegalStateException("unexpected signature " + name + desc);
                patched.add(name);
                return new MethodVisitor(Opcodes.ASM5, mv) {
                    @Override
                    public void visitCode() {
                        super.visitCode();
                        super.visitIincInsn(xz[0], 8);
                        super.visitIincInsn(xz[1], 8);
                    }
                };
            }
        }, 0);
        return cw.toByteArray();
    }

    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) b.write(buf, 0, n);
        return b.toByteArray();
    }
}
