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
    public partial class UploadYoutubeLink : Form
    {
        public const int BYTE_SIZE = 8;
        public const int BINARY_POWER = 2;
        public const int LEN_MSG_LENGTH = 32;
        public const int MESSAGE_CONTENT_INDEX = 40;
        public const int STD_FRAME_JMP = 10;
        public ClientCommunicator _clientCom;

        public UploadYoutubeLink(ClientCommunicator clientCom)
        {
            InitializeComponent();
            _clientCom = clientCom;
        }

        private void UploadYoutubeLink_Load(object sender, EventArgs e)
        {
            comboBox1.Items.Add("Standard prediction");
            comboBox1.Items.Add("Faster prediction");
            comboBox1.Items.Add("Fastest prediction");
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (textBox1.Text == "")
            {
                MessageBox.Show("You have to add a link to the trailer!");
                return;
            }
            else if (comboBox1.SelectedIndex == -1)
            {
                MessageBox.Show("You have to choose an option!");
                return;
            }

            YoutubePredictRequest request = new YoutubePredictRequest
            {
                youtubePath = textBox1.Text,
                frameSector = STD_FRAME_JMP + STD_FRAME_JMP * comboBox1.SelectedIndex
            };
            string jsonPart = JsonConvert.SerializeObject(request);
            string binaryJsonPart = TextUtils.textToBinary(jsonPart);
            string msg = "00000001" + Convert.ToString(jsonPart.Length * BYTE_SIZE, BINARY_POWER)
                .PadLeft(LEN_MSG_LENGTH, '0') +
                binaryJsonPart;

            _clientCom.sendMsgToServer(msg);

            this.Hide();
            LoadingForm window = new LoadingForm(_clientCom);
            window.ShowDialog();
            this.Close();
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            
        }

        private void button2_Click(object sender, EventArgs e)  // back button
        {
            this.Hide();
            OpeningForm window = new OpeningForm(_clientCom);
            window.ShowDialog();
            this.Close();
        }
    }
}
