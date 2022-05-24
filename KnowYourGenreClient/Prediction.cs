using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace KnowYourGenreClient
{
    public partial class Prediction : Form
    {
        public const int PRECENT = 100;
        public ClientCommunicator _clientCom;
        PredicionResponse _response;
        public Prediction(ClientCommunicator clientCom, PredicionResponse response)
        {
            InitializeComponent();
            _clientCom = clientCom;
            _response = response;
        }

        private void Prediction_Load(object sender, EventArgs e)
        {
            chart1.Series["Genres"].Points.AddXY("Horror", (int)(_response.horrorPrediction * PRECENT));
            chart1.Series["Genres"].Points.AddXY("Action", (int)(_response.actionPrediction * PRECENT));
        }

        private void chart1_Click(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)  // back button
        {
            this.Hide();
            UploadYoutubeLink window = new UploadYoutubeLink(_clientCom);
            window.ShowDialog();
            this.Close();
        }
    }
}
