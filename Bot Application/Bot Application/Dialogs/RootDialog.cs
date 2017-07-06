using System;
using System.Threading.Tasks;
using Microsoft.Bot.Builder.Dialogs;
using Microsoft.Bot.Connector;
using System.Net;
using System.IO;
using System.Text;

namespace Bot_Application.Dialogs
{
    [Serializable]
    public class RootDialog : IDialog<object>
    {
        public string MakeRequestToPythonServer(string s)
        {
            string url = "http://23.97.75.47:8000/?q=";
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url + s);
            request.Method = "GET";
            request.ContentType = "text/html;charset=UTF-8";
            HttpWebResponse response = (HttpWebResponse)request.GetResponse();
            Stream stream = response.GetResponseStream();
            StreamReader streamReader = new StreamReader(stream, Encoding.GetEncoding("utf-8"));
            string retString = streamReader.ReadToEnd();
            return retString;
        }


        public Task StartAsync(IDialogContext context)
        {
            context.Wait(MessageReceivedAsync);

            return Task.CompletedTask;
        }

        private async Task MessageReceivedAsync(IDialogContext context, IAwaitable<object> result)
        {
            var activity = await result as Activity;

            // calculate something for us to return
            int length = (activity.Text ?? string.Empty).Length;
            string s = MakeRequestToPythonServer(activity.Text);
            // return our reply to the user
            await context.PostAsync($"{s}");

            context.Wait(MessageReceivedAsync);
        }
    }
   
}