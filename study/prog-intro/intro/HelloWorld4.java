/** 
 * Prints {@code Hello, %arg%!} for each command line argument.
 * The first letter of each {@code %arg%} is capitalized.
 */
public class HelloWorld4 {
    public static String capitalizeFirst(String name) {
        char first = name.charAt(0);
        return Character.toUpperCase(first) + name.substring(1);
    }

    public static void main(String[] args) {
       for (int i = 0; i < args.length; i++) {
           if (args[i].length() >= 3) {
               String capitalized = capitalizeFirst(args[i]);
               System.out.println("Hello, " + capitalized + "!");
           } else {
               System.out.println("Too short: " + args[i]);
               return;
           }
       }
    }
}