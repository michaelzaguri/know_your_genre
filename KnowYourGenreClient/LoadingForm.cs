using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;
using System.Threading;

namespace KnowYourGenreClient
{
    public partial class LoadingForm : Form
    {

        public const int BYTE_SIZE = 8;
        public const int MESSAGE_CONTENT_INDEX = 40;

        public ClientCommunicator _clientCom;
        public string _serverMsg;
        public LoadingForm(ClientCommunicator clientCom)
        {
            InitializeComponent();
            _clientCom = clientCom;
        }

        private void LoadingForm_Load(object sender, EventArgs e)
        {
            
        }

        private void LoadingForm_Shown(object sender, EventArgs e)
        {
            Thread thr = new Thread(new ThreadStart(recieve_message));
            thr.Start();


            thr.Join();
            if (_serverMsg.Substring(0, BYTE_SIZE) == "00000011")  // correct response
            {
                PredicionResponse response = JsonConvert.DeserializeObject<PredicionResponse>
                    (TextUtils.binaryStrToTxt(_serverMsg.Substring(MESSAGE_CONTENT_INDEX)));

                this.Hide();
                Prediction predictionWindow = new Prediction(_clientCom, response);
                predictionWindow.ShowDialog();
                this.Close();
            }
            else if (_serverMsg.Substring(0, BYTE_SIZE) == "00000000")  // error response
            {
                ErrorResponse response = JsonConvert.DeserializeObject<ErrorResponse>
                    (TextUtils.binaryStrToTxt(_serverMsg.Substring(MESSAGE_CONTENT_INDEX)));
                MessageBox.Show(response.error_code);

                this.Hide();
                UploadYoutubeLink window = new UploadYoutubeLink(_clientCom);
                window.ShowDialog();
                this.Close();
            }
        }

        private void recieve_message()
        {
            _serverMsg = _clientCom.readMsgFromServer();
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }
    }
}
