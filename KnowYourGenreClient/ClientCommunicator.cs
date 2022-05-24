using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Net;

namespace KnowYourGenreClient
{
    public class ClientCommunicator
    {
        private NetworkStream clientStream;
        private TcpClient client;
        public const int SERVER_PORT = 2811;
        public const int BUFFER_SIZE = 4096;
        public const string SERVER_IP = "127.0.0.1";

        public void connectToServer()
        {
            client = new TcpClient();
            IPEndPoint serverEndPoint = new IPEndPoint(IPAddress.Parse(SERVER_IP), SERVER_PORT);
            client.Connect(serverEndPoint);
            clientStream = client.GetStream();
        }

        public void endSession()
        {
            clientStream.Close();
            client.Close();
        }

        public void sendMsgToServer(string msg)
        {
            try
            {
                byte[] buffer = new ASCIIEncoding().GetBytes(msg);
                clientStream.Write(buffer, 0, buffer.Length);
                clientStream.Flush();
            }
            catch
            {

            }
        }

        public string readMsgFromServer()
        {
            StringBuilder myCompleteMessage = new StringBuilder();
            if (clientStream.CanRead)
            {
                byte[] myReadBuffer = new byte[BUFFER_SIZE];
                int numberOfBytesRead = 0;

                // Incoming message may be larger than the buffer size.
                do
                {
                    numberOfBytesRead = clientStream.Read(myReadBuffer, 0, myReadBuffer.Length);
                    myCompleteMessage.AppendFormat("{0}", Encoding.ASCII.GetString(myReadBuffer, 0, numberOfBytesRead));
                }
                while (clientStream.DataAvailable);
            }
            else
            {
                return "error";
            }

            return myCompleteMessage.ToString();
        }
    }
}
