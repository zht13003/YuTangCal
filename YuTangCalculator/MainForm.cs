using DevExpress.XtraBars;
using DevExpress.XtraEditors;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;


namespace YuTangCalculator
{
    public partial class MainForm : DevExpress.XtraEditors.XtraForm
    {
        Dictionary<int, string> playerIdToName = new Dictionary<int, string>();
        Dictionary<string, int> playerNameToId = new Dictionary<string, int>();
        Dictionary<string, List<int>> teamToIdList = new Dictionary<string, List<int>>();
        Dictionary<int, int> playerIdToT = new Dictionary<int, int>();
        List<int> redTeamIdList = new List<int>();
        List<int> blueTeamIdList = new List<int>();
        bool rankingMethod = true;
        public MainForm()
        {
            InitializeComponent();
            InitializeTeamInformation();
        }
        private void InitializeTeamInformation()
        {
            using(StreamReader sr = new StreamReader("player.txt"))
            {
                while (!sr.EndOfStream)
                {
                    string teamName = sr.ReadLine().Replace("\n", "");
                    List<int> temp = new List<int>();
                    for(int i = 0; i < 8; i++)
                    {
                        string[] player = sr.ReadLine().Replace("\n", "").Split(',');
                        int id = Convert.ToInt32(player[1]);
                        playerIdToName.Add(id, player[0]);
                        playerIdToT.Add(id, i / 2);
                        playerNameToId.Add(player[0], id);
                        temp.Add(Convert.ToInt32(player[1]));
                    }
                    teamToIdList[teamName] = temp;
                    comboBoxEdit1.Properties.Items.Add(teamName);
                    comboBoxEdit2.Properties.Items.Add(teamName);
                }
            }
        }

        private void ComboBoxEdit1_SelectedValueChanged(object sender, EventArgs e)
        {
            var box = sender as ComboBoxEdit;
            redTeamIdList = teamToIdList[box.Properties.Items[box.SelectedIndex] as string];
        }
        private void ComboBoxEdit2_SelectedValueChanged(object sender, EventArgs e)
        {
            var box = sender as ComboBoxEdit;
            blueTeamIdList = teamToIdList[box.Properties.Items[box.SelectedIndex] as string];
        }

        private void CalculateFromUrl(object sender, EventArgs e)
        {
            var redTeam = new List<Player>();
            var blueTeam = new List<Player>();
            getMatchInformationFromUrl(redTeam, blueTeam);
            showMatchInformation(redTeam, blueTeam);
        }
        private void CalculateFromInput(object sender, EventArgs e)
        {
            var redTeam = new List<Player>();
            var blueTeam = new List<Player>();

            XtraInputBoxArgs args = new XtraInputBoxArgs
            {
                Caption = "由输入读取",
                Prompt = "输入由成绩页面复制的信息（不包括裁判）：",
                DefaultButtonIndex = 0
            };
            MemoEdit editor = new MemoEdit();
            args.Editor = editor;
            var data = XtraInputBox.Show(args);

            if (data != null)
            {
                getMatchInformationFromInput(data.ToString(), redTeam, blueTeam);
                showMatchInformation(redTeam, blueTeam);
            }
        }
        private void toggleSwitch1_Toggled(object sender, EventArgs e)
        {
            var sw = sender as ToggleSwitch;
            rankingMethod = !sw.IsOn;
        }
        private void getMatchInformationFromUrl(List<Player> redTeam, List<Player> blueTeam)
        {
            string mplink = "https://osu.ppy.sh/community/matches/" + textEdit1.Text;
            WebRequest httpWebRequest = WebRequest.Create(mplink);
            httpWebRequest.Method = "GET";
            WebResponse httpWebResponse = httpWebRequest.GetResponse();

            using (StreamReader sr = new StreamReader(httpWebResponse.GetResponseStream(), Encoding.GetEncoding("utf-8")))
            {
                var html = new HtmlAgilityPack.HtmlDocument();
                html.LoadHtml(sr.ReadToEnd().Replace("\n", ""));
                var data = JsonConvert.DeserializeObject<JObject>(html.DocumentNode.SelectSingleNode("//script[@id='json-events']").InnerText);
                var matches = new List<JToken>();
                foreach (var i in data["events"])
                {
                    if (i["detail"]["type"].Value<string>() == "other")
                    {
                        matches.Add(i);
                    }
                }
                var lastMatch = matches.Last()["game"];
                labelControl5.Text = lastMatch["beatmap"]["beatmapset"]["artist_unicode"].Value<string>() + " - " +
                    lastMatch["beatmap"]["beatmapset"]["title_unicode"].Value<string>() + "[" +
                    lastMatch["beatmap"]["version"].Value<string>() + "]";


                foreach (var scores in lastMatch["scores"])
                {
                    int id = scores["user_id"].Value<int>();
                    int score = scores["score"].Value<int>();
                    double acc = scores["accuracy"].Value<double>();
                    if (redTeamIdList.Contains(id))
                    {
                        redTeam.Add(new Player(playerIdToT[id], playerIdToName[id], score, acc));
                    }
                    else if (blueTeamIdList.Contains(id))
                    {
                        blueTeam.Add(new Player(playerIdToT[id], playerIdToName[id], score, acc));
                    }
                    else if(score != 0)
                    {
                        throw new Exception("队伍选择错误！");
                    }
                }
            }
        }
        private void getMatchInformationFromInput(string data, List<Player> redTeam, List<Player> blueTeam)
        {
            string[] temp = data.Split('\n');
            int index = 0;
            while(index < temp.Length)
            {
                temp[index] = temp[index].Replace("\r", "");
                if (temp[index] == string.Empty)
                {
                    index++;
                    continue;
                }
                string name = temp[index];
                int id = playerNameToId[name];
                int score = Convert.ToInt32(temp[index + 6].Replace(",", ""));
                double acc = Convert.ToDouble(temp[index + 4].Replace("%", "")) / 100;
                if (redTeamIdList.Contains(id))
                {
                    redTeam.Add(new Player(playerIdToT[id], name, score, acc));
                }
                else if (blueTeamIdList.Contains(id))
                {
                    blueTeam.Add(new Player(playerIdToT[id], name, score, acc));
                }
                else if (score != 0)
                {
                    throw new Exception("队伍选择错误！");
                }
                index += 15;
            }
        }
        private void showMatchInformation(List<Player> redTeam, List<Player> blueTeam)
        {
            treeList1.Nodes.Clear();
            treeList2.Nodes.Clear();
            int redCount = 0, blueCount = 0;
            foreach (var redPlayer in redTeam)
            {
                var sortedBlueTeam = blueTeam.Append(redPlayer).OrderByDescending(i => i.getScore(rankingMethod));
                redPlayer.setFinalScore(sortedBlueTeam.ToList().FindIndex(p => p == redPlayer) + 1);
            }
            foreach (var bluePlayer in blueTeam)
            {
                var sortedRedTeam = redTeam.Append(bluePlayer).OrderByDescending(i => i.getScore(rankingMethod));
                bluePlayer.setFinalScore(sortedRedTeam.ToList().FindIndex(p => p == bluePlayer) + 1);
            }
            foreach (var redPlayer in redTeam)
            {
                object[][] node = redPlayer.getNodeData();
                treeList1.AppendNode(node[0], -1);
                treeList1.AppendNode(node[1], redCount);
                treeList1.AppendNode(node[2], redCount);
                redCount += 3;
            }
            foreach (var bluePlayer in blueTeam)
            {
                object[][] node = bluePlayer.getNodeData();
                treeList2.AppendNode(node[0], -1);
                treeList2.AppendNode(node[1], blueCount);
                treeList2.AppendNode(node[2], blueCount);
                blueCount += 3;
            }
            labelControl9.Text = string.Format("{0:F1}", redTeam.Sum(p => p.sc));
            labelControl10.Text = string.Format("{0:F1}", blueTeam.Sum(p => p.sc));
            labelControl8.Visible = true;
            if (redTeam.Sum(p => p.sc) > blueTeam.Sum(p => p.sc))
            {
                labelControl8.Text = "红队获胜！";
                labelControl8.Appearance.ForeColor = Color.Red;
            }
            else
            {
                labelControl8.Text = "蓝队获胜！";
                labelControl8.Appearance.ForeColor = Color.Blue;
            }
        }


    }
    class Player
    {
        int T;
        int score;
        string name;
        double acc;
        public double sc;
        public Player(int T, string name, int score, double acc)
        {
            this.T = T;
            this.name = name;
            this.score = score;
            this.acc = acc;
        }
        public void setFinalScore(int rank)
        {
            double sc = 11 - 2 * rank;
            int threshold = 9 - T * 2;
            if(rank == 1)
            {
                if(T == 0)
                {
                    sc = 10;
                }
                else
                {
                    sc = 9.5 - T;
                }
            }
            else if(T != 0 && sc > threshold)
            {
                sc = threshold + (sc - threshold) / 2;
            }
            this.sc = sc;
        }
        public double getScore(bool rankingMethod)
        {
            return rankingMethod ? score : acc;
        }
        public object[][] getNodeData()
        {
            object[][] data = new object[3][];
            data[0] = new object[] { name, sc };
            data[1] = new object[] { "分数", score };
            data[2] = new object[] { "acc", string.Format("{0:F2}%", acc * 100) };
            return data;
        }
    }
}