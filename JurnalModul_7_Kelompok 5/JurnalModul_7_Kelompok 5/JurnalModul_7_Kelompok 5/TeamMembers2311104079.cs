using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace JurnalModul_7_Kelompok_5
{
    public class Member
    {
        public string firstName { get; set; }
        public string lastName { get; set; }
        public string gender { get; set; }
        public int age { get; set; }
        public string nim { get; set; }
    }

    public class TeamMembers2311104079
    {
        public Member[] members { get; set; }

        public void ReadJSON()
        {
            string jsonString = File.ReadAllText("jurnal7_2_2311104079.json");
            TeamMembers2311104079 team = JsonSerializer.Deserialize<TeamMembers2311104079>(jsonString);

            Console.WriteLine("Team member list:");
            foreach (var member in team.members)
            {
                Console.WriteLine($"{member.nim} {member.firstName} {member.lastName} ({member.age} {member.gender})");
            }
        }
    }
}

