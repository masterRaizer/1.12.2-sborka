import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

import java.io.*;
import java.util.*;
import java.util.zip.*;

/**
 * Trinkets and Baubles 0.33.2 + BaublesEX: the "back to Baubles" button in the T&B container (button id 55)
 * sends baubles.common.network.PacketOpenBaublesInventory, a Baubles 1.5.2 class that BaublesEX does not have
 * (NoClassDefFoundError -> client crash on click). This patch replaces
 *     new PacketOpenBaublesInventory()
 * in BaublesHelperFunctions.mousePressedHelper with BaublesEX's
 *     new PacketOpen(PacketOpen.Option.EXPANSION)
 * which opens the Baubles screen the same way. Both are IMessage on the same channel (PacketHandler.INSTANCE).
 * Frames are kept (the jump targets have an empty stack), max stack is recomputed.
 *
 * Usage (Java 8): javac -cp asm-debug-all-5.2.jar -d . PatchXatBex.java
 *                 java -cp "asm-debug-all-5.2.jar;." PatchXatBex <in.jar> <out.jar>
 */
public class PatchXatBex {
    static final String CLS = "xzeroair/trinkets/util/compat/baubles/BaublesHelperFunctions.class";
    static final String OLD = "baubles/common/network/PacketOpenBaublesInventory";
    static final String NEW = "baubles/common/network/PacketOpen";
    static final String OPT = "baubles/common/network/PacketOpen$Option";

    public static void main(String[] a) throws Exception {
        int patched = 0;
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(a[0]));
             ZipOutputStream out = new ZipOutputStream(new FileOutputStream(a[1]))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                byte[] b = readAll(in);
                if (e.getName().equals(CLS)) {
                    ClassNode cn = new ClassNode();
                    new ClassReader(b).accept(cn, 0);
                    for (MethodNode m : cn.methods) {
                        if (!m.name.equals("mousePressedHelper")) continue;
                        for (AbstractInsnNode n : m.instructions.toArray()) {
                            if (n.getOpcode() == Opcodes.NEW && ((TypeInsnNode) n).desc.equals(OLD)) {
                                ((TypeInsnNode) n).desc = NEW;
                            } else if (n.getOpcode() == Opcodes.INVOKESPECIAL && ((MethodInsnNode) n).owner.equals(OLD)) {
                                MethodInsnNode mi = (MethodInsnNode) n;
                                m.instructions.insertBefore(mi, new FieldInsnNode(Opcodes.GETSTATIC, OPT, "EXPANSION", "L" + OPT + ";"));
                                mi.owner = NEW;
                                mi.desc = "(L" + OPT + ";)V";
                                patched++;
                            }
                        }
                    }
                    ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
                    cn.accept(cw);
                    b = cw.toByteArray();
                }
                ZipEntry o = new ZipEntry(e.getName());
                o.setTime(e.getTime());
                out.putNextEntry(o);
                out.write(b);
                out.closeEntry();
            }
        }
        if (patched != 1) throw new IllegalStateException("expected 1 patch site, got " + patched);
        System.out.println("patched " + patched + " site in " + CLS);
    }

    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int r;
        while ((r = in.read(buf)) > 0) bo.write(buf, 0, r);
        return bo.toByteArray();
    }
}
