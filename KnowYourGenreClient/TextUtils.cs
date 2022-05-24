using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace KnowYourGenreClient
{
    class TextUtils
    {
        public const int BYTE_SIZE = 8;
        public const int BINARY_POWER = 2;

        public static string binaryStrToTxt(string buffer)
        {
            int i = 0;
            string realValues = "";
            string curr;
            for (i = 0; i < buffer.Length; i += BYTE_SIZE)
            {
                curr = buffer.Substring(i, BYTE_SIZE);
                realValues += (char)(Convert.ToInt32(curr, BINARY_POWER));
            }
            return realValues;
        }

        public static string textToBinary(string text)
        {
            string binaryText = "";
            foreach (char ch in text)
            {
                binaryText += Convert.ToString((int)ch, BINARY_POWER).PadLeft(BYTE_SIZE, '0');
            }
            return binaryText;
        }
    }
}
