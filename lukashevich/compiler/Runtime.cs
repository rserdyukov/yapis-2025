using System;
using System.Drawing; 

namespace ImageLang
{
    public class SysColor
    {
        public int R, G, B;
        public SysColor(int r, int g, int b) { R = r; G = g; B = b; }
        public Color ToDrawingColor() { return Color.FromArgb(R, G, B); }
        public static SysColor FromDrawingColor(Color c) { return new SysColor(c.R, c.G, c.B); }
    }

    public class SysPixel
    {
        public int x, y;
        private SysImage _img;
        public SysPixel(int x, int y, SysImage img) { this.x = x; this.y = y; this._img = img; }
        public void SetColor(SysColor c) { _img.SetPixel(x, y, c); }
        public SysColor GetColor() { return _img.GetPixel(x, y); }
    }

    public class SysImage
    {
        public Bitmap bmp;
        public SysImage(string path) { 
            try { bmp = new Bitmap(path); } 
            catch { bmp = new Bitmap(10, 10); } 
        }
        public void Save(string path) { bmp.Save(path); }
        public SysColor GetPixel(int x, int y) {
            if (x < 0 || x >= bmp.Width || y < 0 || y >= bmp.Height) return new SysColor(0,0,0);
            return SysColor.FromDrawingColor(bmp.GetPixel(x, y));
        }
        public void SetPixel(int x, int y, SysColor c) {
             if (x >= 0 && x < bmp.Width && y >= 0 && y < bmp.Height)
                bmp.SetPixel(x, y, c.ToDrawingColor());
        }
        public int get_Width() { return bmp.Width; }
        public int get_Height() { return bmp.Height; }
    }

    public static class StdLib
    {
        public static SysImage Load(string path) { return new SysImage(path); }
        public static void Print(object msg) { Console.WriteLine(msg); }
        
        // НОВАЯ ФУНКЦИЯ: Умное сравнение
        public static bool Eq(object a, object b) 
        {
            // Если оба - числа (Double)
            if (a is double && b is double) return Math.Abs((double)a - (double)b) < 0.0001;
            
            // Если оба - цвета
            if (a is SysColor && b is SysColor) {
                var c1 = (SysColor)a; var c2 = (SysColor)b;
                return c1.R == c2.R && c1.G == c2.G && c1.B == c2.B;
            }
            
            // Иначе стандартное сравнение
            return a == b;
        }
    }
}