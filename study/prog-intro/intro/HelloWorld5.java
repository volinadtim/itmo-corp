/** 
 * Greets users specified by command line arguments.
 * The first argument selects a greeting style (either {@code hello} or {@code hi}).
 * The following arguments contain names of the users to greet.
 */
public class HelloWorld5 {
    private static void printUsage() {
        System.out.println("Usage: java HelloWorld5 [hello|hi] <user 1> <user 2> ...");
    }

    public static void main(String[] args) {
        if (args.length <= 1) {
            printUsage();
            return;
        }

        ConsoleGreeter greeter;
        if ("hello".equals(args[0])) {
            greeter = new ConsoleGreeter("Hello, %s!\n");
        } else if ("hi".equals(args[0])) {
            greeter = new ConsoleGreeter("Hi, %s\n");
        } else {
            printUsage();
            return;
        }

        for (int i = 1; i < args.length; i++) {
            greeter.greet(args[i]);
        }
    }
}
