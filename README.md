# 10Internship0Job

<div align="center">
  <img src="https://i.pinimg.com/originals/5b/cf/1b/5bcf1b220433136ccedff7dffc683c29.gif" alt="Logo" />
</div>

 <div align="center" id="contributor">
   <strong>
     <h3> Admin and Members </h3>
     <table align="center">
       <tr align="center">
         <td>NIM</td>
         <td>Name</td>
         <td>GitHub</td>
       </tr>
       <tr align="center">
         <td>13523069</td>
         <td>Mochammad Fariz Rifqi Rizqulloh</td>
         <td><a href="https://github.com/countz-zero">@Fariz36</a></td>
       </tr>
       <tr align="center">
         <td>13523090</td>
         <td>Muhammad Adha Ridwan</td>
         <td><a href="https://github.com/Fariz36">@adharidwan</a></td>
       </tr>
       <tr align="center">
         <td>13523096</td>
         <td>Muhammad Edo</td>
         <td><a href="https://github.com/Nayekah">@poetoeee</a></td>
       </tr>
     </table>
   </strong>
 </div>

 ## ⚙️ Teknologi yang Digunakan
<div align="center">
  
| Teknologi        | Deskripsi                                       |
|------------------|-------------------------------------------------|
| Python           | Bahasa utama                                    |
| Flet             | Framework UI Desktop (berbasis Flutter)         |
| MySQL            | Penyimpanan data pelamar                        |
| PyPDF2/pdfminer  | Ekstraksi teks dari CV PDF                      |
| Regex (re)       | Ekstraksi informasi penting                     |
| Levenshtein      | Pencocokan fuzzy                                |
| KMP, BM          | Algoritma pencocokan string                     |
| Concurrency      | Untuk mempercepat ekstraksi CV dengan threading |

</div>

Sistem ini merupakan aplikasi **CV Applicant Tracking System (ATS) Reviewer** berbasis desktop yang mampu mengekstrak, menyimpan, mencocokkan, dan mencari informasi pelamar kerja secara otomatis menggunakan algoritma pencocokan string dan fuzzy matching. Dibuat sebagai implementasi dari tugas besar mata kuliah IF2211 - Strategi Algoritma.

## ✨ Fitur Utama

### 🔍 Pencarian dan Pencocokan Kata Kunci
- **Exact Matching** menggunakan algoritma:
  - Knuth-Morris-Pratt (KMP)
  - Boyer-Moore (BM)
  - (Bonus) Aho-Corasick
- **Fuzzy Matching** menggunakan **Levenshtein Distance** untuk mencari kata kunci yang tidak cocok secara persis.

### 📄 Ekstraksi Otomatis CV
Menggunakan **Regular Expression (Regex)** untuk mengambil informasi penting dari CV PDF:
- Nama, kontak, dan informasi pribadi
- Ringkasan pelamar (overview)
- Skill
- Pengalaman kerja
- Pendidikan

### 📁 Manajemen dan Penyimpanan Data
- Semua hasil ekstraksi disimpan di **MySQL database**
- Menyimpan informasi pelamar + path file CV

### 🖥️ Antarmuka Pengguna
Dibuat dengan framework **Flet** (Python UI modern dan responsif)

Fitur interaktif meliputi:
- Input kata kunci
- Pemilihan algoritma pencocokan
- Pemilihan jumlah hasil CV yang ingin ditampilkan
- Ringkasan pelamar per hasil pencarian
- Tombol untuk membuka file CV lengkap
- Statistik waktu pencarian (exact & fuzzy)

## Installation & Setup
 
### Requirements
 > - Python
 > - UV package manager (better than pip)
 > - Docker

### 1. Clone Repository
```bash
git clone https://github.com/Fariz36/Tubes3_10Internship0Job.git
cd Tubes3_10Internship0Job/src
uv sync
(LINUX)
cd ../database
docker compose up -d
(WINDOWS)
cd ../database
sudo docker-compose up -d
cd ../src
uv run ./app/main.py
```


 <br/>
 <br/>
 <br/>
 <br/>
 
 <div align="center">
 Strategi Algoritma • © 2025 • 10Internship0Job
 </div>
