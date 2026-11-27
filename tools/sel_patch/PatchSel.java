import java.io.*;
import java.util.*;
import java.util.zip.*;
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;

/** Patch Smooth Entity Light 4.0.4: auto block light for held/dropped items + acceptableRemoteVersions="*".
 *  java -cp "asm-debug-all-5.2.jar;." PatchSel in.jar SELAutoLight.class out.jar */
public class PatchSel {
    static final String HELPER = "lakmoore/sel/client/ItemConfigHelper";
    static final String SEL = "lakmoore/sel/client/SEL";
    static final String AUTO = "lakmoore/sel/client/SELAutoLight";

    public static void main(String[] a) throws Exception {
        byte[] auto = readAll(new FileInputStream(a[1]));
        int done = 0;
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(a[0]));
             ZipOutputStream out = new ZipOutputStream(new FileOutputStream(a[2]))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                String n = e.getName();
                byte[] d = readAll(in);
                if (n.startsWith("META-INF/fml_cache_")) continue;
                if (n.equals(HELPER + ".class")) { d = patchHelper(d); done++; }
                else if (n.equals(SEL + ".class")) { d = patchSel(d); done++; }
                out.putNextEntry(new ZipEntry(n));
                out.write(d);
                out.closeEntry();
            }
            out.putNextEntry(new ZipEntry(AUTO + ".class"));
            out.write(auto);
            out.closeEntry();
        }
        if (done != 2) throw new IllegalStateException("patched " + done + " of 2 classes");
        System.out.println("OK");
    }

    static byte[] patchHelper(byte[] d) {
        ClassNode cn = new ClassNode();
        new ClassReader(d).accept(cn, 0);
        boolean ok = false;
        for (MethodNode m : cn.methods) {
            if (m.name.equals("getLightFromItemStack") && m.desc.equals("(Lnet/minecraft/item/ItemStack;)I")) {
                m.instructions.clear();
                m.tryCatchBlocks.clear();
                m.localVariables = null;
                m.visibleLocalVariableAnnotations = null;
                m.instructions.add(new VarInsnNode(Opcodes.ALOAD, 0));
                m.instructions.add(new VarInsnNode(Opcodes.ALOAD, 1));
                m.instructions.add(new MethodInsnNode(Opcodes.INVOKESTATIC, AUTO, "get",
                        "(L" + HELPER + ";Lnet/minecraft/item/ItemStack;)I", false));
                m.instructions.add(new InsnNode(Opcodes.IRETURN));
                m.maxStack = 2; m.maxLocals = 2;
                ok = true;
            }
        }
        if (!ok) throw new IllegalStateException("getLightFromItemStack not found");
        ClassWriter cw = new ClassWriter(ClassWriter.COMPUTE_MAXS);
        cn.accept(cw);
        return cw.toByteArray();
    }

    static byte[] patchSel(byte[] d) {
        ClassNode cn = new ClassNode();
        new ClassReader(d).accept(cn, 0);
        boolean ok = false;
        for (AnnotationNode an : cn.visibleAnnotations) {
            if (an.desc.equals("Lnet/minecraftforge/fml/common/Mod;")) {
                if (an.values == null) an.values = new ArrayList<Object>();
                if (an.values.contains("acceptableRemoteVersions")) throw new IllegalStateException("already set");
                an.values.add("acceptableRemoteVersions");
                an.values.add("*");
                ok = true;
            }
        }
        if (!ok) throw new IllegalStateException("@Mod not found");
        ClassWriter cw = new ClassWriter(0);
        cn.accept(cw);
        return cw.toByteArray();
    }

    static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        byte[] buf = new byte[8192]; int r;
        while ((r = in.read(buf)) > 0) b.write(buf, 0, r);
        return b.toByteArray();
    }
}
