using JurnalModul_7_Kelompok_5;
using System;


class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("========== Deserialisasi Data Mahasiswa ==========");
        var dataMahasiswa = new DataMahasiswa2311104079();
        dataMahasiswa.ReadJSON();

        Console.WriteLine("\n========== Deserialisasi Team Members ==========");
        var teamMembers = new TeamMembers2311104079();
        teamMembers.ReadJSON();

        Console.WriteLine("\n========== Deserialisasi Glossary Item ==========");
        var glossaryItem = new GlossaryItem2311104079();
        glossaryItem.ReadJSON();
        Console.ReadLine();
    }
}