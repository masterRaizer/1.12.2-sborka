import org.objectweb.asm.*;

import java.io.*;
import java.util.zip.*;

/**
 * htc_reactors 1.0.0 (VoidStudio HiTech, Java 8 build "-j8"): blocks are missing on a dedicated server.
 *
 * The mod registers its blocks, their ItemBlocks and 4 TileEntities in
 * client/registry/RegistryBlocks.registerBlocks(RegistryEvent.Register<Block>), and only
 * client/ClientProxy.<init> subscribes that handler to MinecraftForge.EVENT_BUS. CommonProxy.<init> subscribes
 * only RegistryItems, and server/ServerProxy (an empty class added by tools/ic2_hitech/addproxy.py, the original
 * mod has no server proxy) only calls super(). So on a dedicated server htc_reactors:nuclear_reactor,
 * nanite_complex, nanite_configuration_bench, nanite_modification_station, reactor_casing, nanite_casing never
 * exist.
 *
 * This patch makes ServerProxy.<init> do the same as ClientProxy:
 *     super(); MinecraftForge.EVENT_BUS.register(new RegistryBlocks());
 * ClientProxy/CommonProxy are not touched, so the client registers exactly as before (no double subscription).
 * RegistryBlocks has no @SideOnly and no client types in method signatures; the client-only calls
 * (ModelLoader, ModelBakery) are inside registerBlockModel(), which only ClientProxy's ModelRegistryEvent calls.
 *
 * Usage (Java 8 bytecode): javac --release 8 -cp asm-debug-all-5.2.jar PatchHtcReactors.java
 *                          java -cp asm-debug-all-5.2.jar;. PatchHtcReactors <in.jar> <out.jar>
 */
public class PatchHtcReactors {
    static final String PROXY = "ru/thetzddark/htc_reactors/server/ServerProxy";
    static final String SUPER = "ru/thetzddark/htc_reactors/common/CommonProxy";
    static final String REG = "ru/thetzddark/htc_reactors/client/registry/RegistryBlocks";
    static final String FORGE = "net/minecraftforge/common/MinecraftForge";
    static final String BUS = "net/minecraftforge/fml/common/eventhandler/EventBus";

    static int patched = 0;

    public static void main(String[] a) throws Exception {
        try (ZipInputStream in = new ZipInputStream(new FileInputStream(a[0]));
             ZipOutputStream out = new ZipOutputStream(new FileOutputStream(a[1]))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                byte[] data = readAll(in);
                if (e.getName().equals(PROXY + ".class")) data = patch(data);
                out.putNextEntry(new ZipEntry(e.getName()));
                out.write(data);
                out.closeEntry();
            }
        }
        if (patched != 1) {
            new File(a[1]).delete();
            throw new IllegalStateException("ServerProxy.<init> patched " + patched + " times, expected 1");
        }
        System.out.println("patched: " + PROXY + ".<init> registers " + REG);
    }

    static byte[] patch(byte[] cls) {
        ClassReader cr = new ClassReader(cls);
        if (!SUPER.equals(cr.getSuperName())) throw new IllegalStateException("unexpected super " + cr.getSuperName());
        ClassWriter cw = new ClassWriter(cr, ClassWriter.COMPUTE_MAXS);
        cr.accept(new ClassVisitor(Opcodes.ASM5, cw) {
            @Override
            public MethodVisitor visitMethod(int acc, String name, String desc, String sig, String[] ex) {
                MethodVisitor mv = super.visitMethod(acc, name, desc, sig, ex);
                if (!name.equals("<init>") || !desc.equals("()V")) return mv;
                return new MethodVisitor(Opcodes.ASM5, mv) {
                    boolean done;

                    @Override
                    public void visitMethodInsn(int op, String owner, String n, String d, boolean itf) {
                        super.visitMethodInsn(op, owner, n, d, itf);
                        if (op == Opcodes.INVOKESPECIAL && owner.equals(SUPER) && n.equals("<init>") && !done) {
                            // MinecraftForge.EVENT_BUS.register(new RegistryBlocks());
                            super.visitFieldInsn(Opcodes.GETSTATIC, FORGE, "EVENT_BUS", "L" + BUS + ";");
                            super.visitTypeInsn(Opcodes.NEW, REG);
                            super.visitInsn(Opcodes.DUP);
                            super.visitMethodInsn(Opcodes.INVOKESPECIAL, REG, "<init>", "()V", false);
                            super.visitMethodInsn(Opcodes.INVOKEVIRTUAL, BUS, "register", "(Ljava/lang/Object;)V", false);
                            done = true;
                            patched++;
                        }
                    }

                    @Override
                    public void visitMethodInsn(int op, String owner, String n, String d) {
                        visitMethodInsn(op, owner, n, d, op == Opcodes.INVOKEINTERFACE);
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
