using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace KnowYourGenreClient
{
    public class YoutubePredictRequest
    {
        public string youtubePath { set; get; }  // the path to the trailer through youtube
        public int frameSector { set; get; }  // the jump between each frame that is taken
    }
}
