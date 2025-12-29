// StringLangRuntime.java

import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

public class StringLangRuntime {
    private static Scanner scanner = new Scanner(System.in);
    
    public static String readString() {
        if (scanner.hasNextLine()) {
            return scanner.nextLine();
        }
        return "";
    }
    
    public static void writeValue(String value) {
        System.out.print(value);
    }
    
    public static String removeSubstring(String str, String sub) {
        int index = str.indexOf(sub);
        if (index >= 0) {
            return str.substring(0, index) + str.substring(index + sub.length());
        }
        return str;
    }
    
    public static String repeatString(String str, String count) {
        int n = count.length();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            sb.append(str);
        }
        return sb.toString();
    }
    
    public static String[] splitString(String str, String delimiter) {
        if (delimiter.isEmpty()) {
            String[] result = new String[str.length()];
            for (int i = 0; i < str.length(); i++) {
                result[i] = String.valueOf(str.charAt(i));
            }
            return result;
        }
        return str.split(java.util.regex.Pattern.quote(delimiter));
    }
    
    public static boolean stringIn(String needle, String haystack) {
        return haystack.contains(needle);
    }
    
    public static boolean stringLessThan(String a, String b) {
        return a.compareTo(b) < 0;
    }
    
    public static boolean stringGreaterThan(String a, String b) {
        return a.compareTo(b) > 0;
    }
    
    public static int stringLength(String str) {
        return str.length();
    }
    
    public static String substring(String str, int from, int len) {
        if (from < 0 || from + len > str.length()) {
            return "";
        }
        return str.substring(from, from + len);
    }
    
    public static String replace(String str, String oldStr, String newStr) {
        return str.replace(oldStr, newStr);
    }
    
    public static String indexString(String str, int index) {
        if (index < 0 || index >= str.length()) {
            return "";
        }
        return String.valueOf(str.charAt(index));
    }
    
    public static String indexArray(String[] arr, int index) {
        if (index < 0 || index >= arr.length) {
            return "";
        }
        return arr[index];
    }
}