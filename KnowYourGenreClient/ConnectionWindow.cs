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
    public partial class ConnectionWindow : Form
    {
        public ClientCommunicator clientCom;
        public ConnectionWindow()
        {
            InitializeComponent();
        }

        private void ConnectionWindow_Load(object sender, EventArgs e)
        {
            clientCom = new ClientCommunicator();

            try
            {
                clientCom.connectToServer();
                this.Hide();
                OpeningForm window = new OpeningForm(clientCom);
                window.ShowDialog();
                this.Close();
            }
            catch
            {
                MessageBox.Show("Couldn't connect to the server!");
                this.Close();
            }
        }
    }
}
