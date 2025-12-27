using System;
using System.Collections.Generic;
using System.Linq;

namespace SetLangRuntime {
    public static class Ops {

        public static object BuiltinCount(object collection, object item) {
            if (collection == null) throw new Exception("count(): collection is null");

            if (collection is List<object>) {
                var list = (List<object>)collection;
                int occurrences = 0;
                foreach (var x in list) {
                    if (x != null && x.Equals(item)) {
                        occurrences++;
                    } else if (x == null && item == null) {
                        occurrences++;
                    }
                }
                return (object)occurrences;
            }


            throw new Exception("count() works only with Tuple");
        }

         public static object BuiltinAdd(object collection, object item) {
             if (collection is HashSet<object>) {
                 var newSet = new HashSet<object>((HashSet<object>)collection);
                 newSet.Add(item);
                 return newSet;
             }
             if (collection is List<object>) {
                 var newList = new List<object>((List<object>)collection);
                 newList.Add(item);
                 return newList;
             }
             throw new Exception("add() works only with Set or Tuple");
         }

         public static object BuiltinDelete(object collection, object item) {
             if (collection is HashSet<object>) {
                 var newSet = new HashSet<object>((HashSet<object>)collection);
                 newSet.Remove(item);
                 return newSet;
             }
             if (collection is List<object>) {
                 var newList = new List<object>((List<object>)collection);
                 newList.Remove(item);
                 return newList;
             }
             throw new Exception("delete() works only with Set or Tuple");
         }
         public static object BuiltinIncludes(object collection, object item) {
                    bool found = false;
                    if (collection is HashSet<object>) found = ((HashSet<object>)collection).Contains(item);
                    else if (collection is List<object>) found = ((List<object>)collection).Contains(item);
                    else throw new Exception("includes() works only with Set or Tuple");
                    return (object)found;
                }

         public static object BuiltinLen(object collection) {
                    if (collection is HashSet<object>) return (object)((HashSet<object>)collection).Count;
                    if (collection is List<object>) return (object)((List<object>)collection).Count;
                    throw new Exception("len() works only with Set or Tuple");
                }


         private static string FormatItem(object x) {
                    if (x == null) return "null";
                    if (x is string) return "\"" + x + "\"";
                    if (x is bool) return x.ToString().ToLower();
                    if (x is HashSet<object>) return "{...}";
                    if (x is List<object>) return "[...]";
                    return x.ToString();
                }

        private static void EnsureNotNull(object a, object b, string op) {
            if (a == null || b == null) {
                throw new Exception("Runtime Error: Variable is null in operation '" + op + "'.");
            }
        }

        public static bool ToBool(object a) {
            if (a == null) return false;
            if (a is bool) return (bool)a;
            if (a is int) return (int)a != 0;
            if (a is HashSet<object>) return ((HashSet<object>)a).Count > 0;
            if (a is List<object>) return ((List<object>)a).Count > 0;
            if (a is string) return ((string)a).Length > 0;
            return true;
        }


        public static object Add(object a, object b) {
            EnsureNotNull(a, b, "+");
            if (a is int && b is int) return (int)a + (int)b;
            if (a is string || b is string) return a.ToString() + b.ToString();
            if (a is HashSet<object> && b is HashSet<object>) {
                var res = new HashSet<object>((HashSet<object>)a);
                res.UnionWith((HashSet<object>)b);
                return res;
            }
            if (a is List<object> && b is List<object>) {
                var res = new List<object>((List<object>)a);
                res.AddRange((List<object>)b);
                return res;
            }
            throw new Exception("Type mismatch for +");
        }

        public static object Sub(object a, object b) {
            EnsureNotNull(a, b, "-");
            if (a is int && b is int) return (int)a - (int)b;
            if (a is HashSet<object> && b is HashSet<object>) {
                var res = new HashSet<object>((HashSet<object>)a);
                res.ExceptWith((HashSet<object>)b);
                return res;
            }
            if (a is List<object> && b is List<object>) {
                var la = (List<object>)a; var lb = (List<object>)b;
                return la.Where(x => !lb.Contains(x)).ToList();
            }
            throw new Exception("Type mismatch for -");
        }

        public static object Mul(object a, object b) {
            EnsureNotNull(a, b, "*");
            if (a is int && b is int) return (int)a * (int)b;
            if (a is HashSet<object> && b is HashSet<object>) {
                var res = new HashSet<object>((HashSet<object>)a);
                res.IntersectWith((HashSet<object>)b);
                return res;
            }
            if (a is List<object> && b is List<object>) {
                var la = (List<object>)a; var lb = (List<object>)b;
                return la.Where(x => lb.Contains(x)).Distinct().ToList();
            }
            throw new Exception("Type mismatch for *");
        }

        public static object Div(object a, object b) {
            EnsureNotNull(a, b, "/");
            if (a is int && b is int) return (int)a / (int)b;
            if (a is HashSet<object> && b is HashSet<object>) {
                var res = new HashSet<object>((HashSet<object>)a);
                res.SymmetricExceptWith((HashSet<object>)b);
                return res;
            }
            if (a is List<object> && b is List<object>) {
                var setA = new HashSet<object>((List<object>)a);
                var setB = new HashSet<object>((List<object>)b);
                setA.SymmetricExceptWith(setB);
                return setA.ToList();
            }
            throw new Exception("Type mismatch for /");
        }

        public static bool Compare(object a, object b, string op) {
            EnsureNotNull(a, b, op);
            if (a is int && b is int) {
                int ia = (int)a; int ib = (int)b;
                if (op == "<") return ia < ib;
                if (op == ">") return ia > ib;
                if (op == "<=") return ia <= ib;
                if (op == ">=") return ia >= ib;
                if (op == "==") return ia == ib;
                if (op == "!=") return ia != ib;
            }
            if (a is HashSet<object> && b is HashSet<object>) {
                var sa = (HashSet<object>)a; var sb = (HashSet<object>)b;
                if (op == "<") return sa.IsProperSubsetOf(sb);
                if (op == "<=") return sa.IsSubsetOf(sb);
                if (op == ">") return sa.IsProperSupersetOf(sb);
                if (op == ">=") return sa.IsSupersetOf(sb);
                if (op == "==") return sa.SetEquals(sb);
                if (op == "!=") return !sa.SetEquals(sb);
            }
            if (a is List<object> && b is List<object>) {
                var la = (List<object>)a; var lb = (List<object>)b;
                if (op == "==") return la.SequenceEqual(lb);
                if (op == "!=") return !la.SequenceEqual(lb);
                if (op == "<=") return la.All(x => lb.Contains(x));
                if (op == ">=") return lb.All(x => la.Contains(x));
            }
            if (op == "==") return a.Equals(b);
            if (op == "!=") return !a.Equals(b);
            throw new Exception("Compare mismatch");
        }

        public static bool LogicalOp(object a, object b, string op) {
            bool ba = ToBool(a);
            bool bb = ToBool(b);
            return (op == "&&") ? (ba && bb) : (ba || bb);
        }

        public static bool Not(object a) {
            return !ToBool(a);
        }

         public static object BuiltinPrint(object obj) {
                    Console.WriteLine(Stringify(obj, 0));
                    return obj;
                }

         public static string Stringify(object obj, int depth) {
                    if (depth > 10) return "{...}";

                    if (obj == null) return "null";

                    if (obj is string) return "\"" + obj + "\"";

                    if (obj is bool) return obj.ToString().ToLower();

                    if (obj is HashSet<object>) {
                        var s = (HashSet<object>)obj;
                        if (s.Count == 0) return "{}";

                        var elements = new List<string>();
                        foreach (var item in s) {
                            elements.Add(Stringify(item, depth + 1));
                        }
                        return "{" + string.Join(", ", elements.ToArray()) + "}";
                    }

                    if (obj is List<object>) {
                        var l = (List<object>)obj;
                        if (l.Count == 0) return "[]";

                        var elements = new List<string>();
                        foreach (var item in l) {
                            elements.Add(Stringify(item, depth + 1));
                        }
                        return "[" + string.Join(", ", elements.ToArray()) + "]";
                    }

                    return obj.ToString();
                }

    }
}