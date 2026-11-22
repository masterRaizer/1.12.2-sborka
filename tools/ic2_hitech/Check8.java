import java.io.*; import java.lang.reflect.*; import java.util.*;
public class Check8 {
  public static void main(String[] a) throws Exception {
    BufferedReader r = new BufferedReader(new FileReader(a[0])); String l; int bad = 0;
    while ((l = r.readLine()) != null) {
      String[] p = l.split(" "); String owner = p[1].replace('/', '.'); String name = p[2]; String desc = p[3];
      Class<?> c; try { c = Class.forName(owner.startsWith("[") ? owner : owner, false, null); } catch (Throwable t) { System.out.println("MISSING CLASS " + l); bad++; continue; }
      if (p[0].equals("9")) { boolean f=false; for (Class<?> k=c;k!=null&&!f;k=k.getSuperclass()) for (Field x: k.getDeclaredFields()) if (x.getName().equals(name)) f=true; if(!f){System.out.println("MISSING FIELD "+l);bad++;} continue; }
      boolean found = false;
      Deque<Class<?>> q = new ArrayDeque<>(); q.add(c); Set<Class<?>> seen = new HashSet<>();
      while (!q.isEmpty() && !found) { Class<?> k = q.poll(); if (!seen.add(k)) continue;
        if (name.equals("<init>")) { for (Constructor<?> x : k.getDeclaredConstructors()) if (sig(x.getParameterTypes(), void.class).equals(desc)) found = true; }
        else for (Method x : k.getDeclaredMethods()) if (x.getName().equals(name) && sig(x.getParameterTypes(), x.getReturnType()).equals(desc)) found = true;
        if (k.getSuperclass() != null) q.add(k.getSuperclass()); q.addAll(Arrays.asList(k.getInterfaces())); if (k.isInterface()) q.add(Object.class); }
      if (!found) { System.out.println("MISSING METHOD " + l); bad++; }
    }
    System.out.println("checked, missing=" + bad);
  }
  static String d(Class<?> c) { if (c.isArray()) return "[" + d(c.getComponentType()); if (c.isPrimitive()) { if (c==void.class) return "V"; if (c==int.class) return "I"; if (c==long.class) return "J"; if (c==boolean.class) return "Z"; if (c==byte.class) return "B"; if (c==char.class) return "C"; if (c==short.class) return "S"; if (c==float.class) return "F"; return "D"; } return "L" + c.getName().replace('.', '/') + ";"; }
  static String sig(Class<?>[] ps, Class<?> rt) { StringBuilder b = new StringBuilder("("); for (Class<?> p : ps) b.append(d(p)); return b.append(")").append(d(rt)).toString(); }
}
