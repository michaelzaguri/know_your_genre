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
    public partial class OpeningForm : Form
    {
        public ClientCommunicator _clientCom;

        public OpeningForm(ClientCommunicator clientCom)
        {
            InitializeComponent();
            _clientCom = clientCom;
        }

        private void OpeningForm_Load(object sender, EventArgs e)
        {
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.Hide();
            UploadYoutubeLink youtubwWindow = new UploadYoutubeLink(_clientCom);
            youtubwWindow.ShowDialog();
            this.Close();
        }
    }
}
