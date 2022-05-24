using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace KnowYourGenreClient
{
    public class PredicionResponse
    {
        public float actionPrediction { set; get; }  // the prediction of the server for actoin
        public float horrorPrediction { set; get; }  // the prediction of the server for horror
    }

    public class ErrorResponse
    {
        public string error_code { set; get; }  // the error the server sent
    }
}   
