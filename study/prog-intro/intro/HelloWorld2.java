/** 
 * Prints {@code Hello, %arg%!} on the console. 
 * Where {@code %arg%} is the value of the first command-line argument.
 */
public class HelloWorld2 {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java HelloWorld2 <user name>");
            return;
        }
        System.out.printf("Hello, %s!", args[0]);
    }
}
