using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace JurnalModul_7_Kelompok_5
{
        public class Address
        {
            public string streetAddress { get; set; }
            public string city { get; set; }
            public string state { get; set; }
        }

        public class Course
        {
            public string code { get; set; }
            public string name { get; set; }
        }

        public class DataMahasiswa2311104079
        {
            public string firstName { get; set; }
            public string lastName { get; set; }
            public string gender { get; set; }
            public int age { get; set; }
            public Address address { get; set; }
            public Course[] courses { get; set; }

            public void ReadJSON()
            {
                string jsonString = File.ReadAllText("jurnal7_1_2311104079.json");
                DataMahasiswa2311104079 mahasiswa = JsonSerializer.Deserialize<DataMahasiswa2311104079>(jsonString);

                Console.WriteLine($"Nama: {mahasiswa.firstName} {mahasiswa.lastName}");
                Console.WriteLine($"Gender: {mahasiswa.gender}");
                Console.WriteLine($"Age: {mahasiswa.age}");
                Console.WriteLine($"Address: {mahasiswa.address.streetAddress}, {mahasiswa.address.city}, {mahasiswa.address.state}");
                Console.WriteLine("Courses:");
                foreach (var course in mahasiswa.courses)
                {
                    Console.WriteLine($"- {course.code}: {course.name}");
                }
            }
        }
    }

