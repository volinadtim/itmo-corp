public class Sum {
    public static void main(String[] args) {
        int res = 0;
        for (String arg : args) {
            String[] parts = arg.strip().split("\\p{javaWhitespace}+");
            for (var part : parts)
                if(part != "")
                res += Integer.parseInt(part);
        }
        System.out.println(res);
    }
}
