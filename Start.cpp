#include <iostream>
#include <windows.h>
#include <mysql.h>
#include <string.h>
#include <fstream>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include "stemming/english_stem.h"

using namespace std;
string id,gfname,glname,phone,gemail,age,resume_name;

class FileProcessor {
private:
    string input_filename, resume_filename, p_resume_filename, txt = ".txt", ptxt = "_processed.txt", space = " ";
    ifstream resume_file, stopword_file; // Open the files under these names.
    ofstream processed_resume_file;     // To store the processed Resume File.
    char resume_word[50];
    char contact[14], fname[20] , lname[20], email[40];
    string sw = "stopwords.txt";     // File containing stop words.

    void CaseLower(char *);     // To change words to lower Case.
    char *FindNumber();

    void FindName();

    char *FindEmail();

public:
    void StopWord(string);            // To remove stop words.
    void FindDetails();         // To extract details such as names,Contact no. etc
    void RemoveComma(char[]);
    void stem_func(char[]);
};


void FileProcessor::FindDetails() {
    int qstate;
    MYSQL* conn;
    string sname, pros_resume_name;
    resume_file.open(p_resume_filename.c_str());
    cout<<endl<<"Extracted details are:"<<endl;
    if (!resume_file.is_open()) {
        exit(EXIT_FAILURE);
    }
    strcpy(contact, FindNumber());
    cout << endl << contact << endl;   //  ************************************************

    resume_file.clear();
    resume_file.seekg(0, ios::beg);

    strcpy(email, FindEmail());
    cout << endl << email << endl;   //  ************************************************

    resume_file.clear();
    resume_file.seekg(0, ios::beg);

    FindName();
    cout << endl << lname << " " << fname << endl;   //  ************************************************


    // Global Assignment

    gfname = fname;
    glname = lname;
    gemail = email;
    phone  = contact;

    resume_file.close();
}


char *FileProcessor::FindNumber()      // NUMBER
{
    char *word, flag = 'f', num[14];
    resume_file.clear();
    resume_file.seekg(0,ios::beg);
    while (resume_file.good()) {
        resume_file >> resume_word;
        word = resume_word;
        if (strlen(word) >= 10) {
            if (word[0] == '+' || (word[0] >= 48 && word[0] <= 57)) {
                flag = 't';
                break;
            }
        }
    }
    if (flag == 't'){
        return word;
    }
    else
        return "NA";
}

char *FileProcessor::FindEmail()        // E-MAIL
{
    size_t i;
    char *word, email[40];
    while (resume_file.good()) {
        resume_file >> resume_word;
        word = resume_word;
        for (i = 0; i < strlen(word); i++) {
            if (word[i] == '@') {
                strcpy(email,word);
                return email;
            }
        }
    }
    return "NA";
}


void FileProcessor::FindName()        // NAME
{
    size_t i, count = 0;
    char *word, flag;
    while (resume_file.good()) {
        if (count > 1)
            break;
        resume_file >> resume_word;
        word = resume_word;
        for (i = 0; i < strlen(word); i++) {
            if (((word[i] >= 65 && word[i] <= 90) ||
                 (word[i] >= 97 && word[i] <= 122))) {                       // Not a letter of Alphabet
                flag = 't';
            } else {
                flag = 'f';
                break;
            }
        }
        if (count == 1 && flag == 't') {
            strcpy(lname , word);
            if (islower(lname[0])) lname[0] = toupper(lname[0]);
            count++;
        } else if (count == 0 && flag == 't') {
            strcpy(fname , word);
            if (islower(fname[0])) fname[0] = toupper(fname[0]);
            count++;

        }
    }
}


void FileProcessor::CaseLower(char *word) {
    for (size_t i = 0; i < strlen(word); i++) {
        if (isupper(word[i])) word[i] = tolower(word[i]);
    }
}

void FileProcessor::StopWord(string x) {


    cin.clear();
    //cin >> input_filename;  // Enter the name of the Resume File.
    input_filename = x;
    resume_filename = "C:\\Users\\Parthmaheswari\\Documents\\c language\\Minor2\\Resume\\" + input_filename + txt;

    p_resume_filename = input_filename + ptxt;

    resume_file.open(resume_filename.c_str());
    if (!resume_file.is_open()) {
        exit(EXIT_FAILURE);
    }

    char stop_word[50];

    stopword_file.open(sw.c_str());
    if (!stopword_file.is_open()) {

        exit(EXIT_FAILURE);
    }
    int is_a_stop_word;

    processed_resume_file.open(p_resume_filename.c_str());
    if (!processed_resume_file.is_open()) {
        exit(EXIT_FAILURE);
    }

    while (resume_file.good()) {
        resume_file >> resume_word;
        CaseLower(resume_word);
        RemoveComma(resume_word);
        stem_func(resume_word);
        is_a_stop_word = 0;
        stopword_file.clear();
        stopword_file.seekg(0, ios::beg);
        stopword_file >> stop_word;

        while (stopword_file.good()) {
            if (std::strcmp(resume_word, stop_word) == 0) // if it is a stop word.
            {
                is_a_stop_word = 1;
                break;
            }
            stopword_file >> stop_word;
        }
        if (is_a_stop_word) {
            resume_file >> resume_word;
            continue;
        }
        processed_resume_file << resume_word;
        processed_resume_file << space;
    }
    FindDetails();
    resume_file.close();
    stopword_file.close();
    processed_resume_file.close();

    system("PAUSE");

}

void FileProcessor::RemoveComma(char word[])
{
    for(int i=0;i<50;i++)
    {
        if(word[i]==','||word[i]==';')
            word[i] = ' ';
    }
}

void FileProcessor::stem_func(char *input){
    //string input;
    //cin>>input;
    string str(input);
    wstring str2(str.length(), L' ');
    copy(str.begin(), str.end(), str2.begin());
    wstring word(str2);
    stemming::english_stem<> StemEnglish;
    //wcout << L"(English) Original text:\t" << word.c_str() << endl;
    StemEnglish(word);
    //wcout << L"(English) Stemmed text:\t" << word.c_str() << endl;
}

int main()
{
    FileProcessor worker;
    MYSQL_ROW row;
    MYSQL_RES *res;
    char cont;
    int qstate;
    int choice;
    MYSQL* conn;

    conn = mysql_init(0);

    conn = mysql_real_connect(conn,"localhost","root","","recruitment",0,NULL,0);
    do {
        if (conn) {
            cout << "Welcome to Recruitment Portal" << endl;
            cout << "Connection to database successful " << endl;
            cout << "Enter your choice:" << endl;
            cout << "1. Insert a record" << endl;
            cout << "2. Delete a record" << endl;
            cout << "3. Search for a record" << endl;
            cout << "4. Display all records" << endl;
            cout << "5. Filter records" << endl;
            //cout<<"6. Process resume"<<endl;
            cin >> choice;

            switch (choice) {

                case (1) : {

                    cout << "Enter EnrollmentId: " << endl;
                    cin >> id;
                    //cout<<"Enter First Name: "<<endl; //cin>>fname;
                    //cout<<"Enter Last Name: "<<endl; //cin>>lname;
                    //cout<<"Enter MobileNo: "<<endl; //cin>>phone;
                    //cout<<"Enter Email: "<<endl; //cin>>email;
                    //cout<<"Enter Resume: "<<endl; cin>>resume_name;

                    string proc_resume;
                    proc_resume = id + "_processed";

                    worker.StopWord(id);

                    string query =
                            "insert into recruitment_info(FName,LName,Mob,Email,EnrollmentID,Resume,ProcessedResume) values('" +
                            gfname + "','" + glname + "','" + phone + "','" + gemail + "','" + id + "','" + id + "','" +
                            proc_resume + "')";

                    const char *q = query.c_str();

                    cout << "query is: " << q << endl << endl;
                    qstate = mysql_query(conn, q);

                    if (!qstate) {
                        cout << "record inserted successfully..." << endl;
                    } else
                        cout << "query problem: " << mysql_error(conn) << endl;
                }

                    break;


                case (2) : {
                    string delete_id, delete_query;
                    cout << "Enter Enrollment number of student to be deleted" << endl;
                    cin >> delete_id;
                    delete_query = "delete from recruitment_info where EnrollmentID = " + delete_id;
                    qstate = mysql_query(conn, delete_query.c_str());
                    if (!qstate)
                        cout << "record deleted successfully..." << endl;
                    else
                        cout << "query problem: " << mysql_error(conn) << endl;
                }

                    break;

                case (3) : {
                    string rno, resume_query, open_loc;
                    char x[20];
                    ifstream inFile;
                    cout << "Enter Enrollment number" << endl;
                    cin >> rno;
                    resume_query = "select Resume from recruitment_info where EnrollmentId = " + rno;
                    qstate = mysql_query(conn, resume_query.c_str());
                    if (!qstate) {
                        res = mysql_store_result(conn);
                        row = mysql_fetch_row(res);
                        cout << "File name is " << row[0] << ".txt" << endl << endl;
                    } else
                        cout << "query error: " << mysql_error(conn) << endl;

                    open_loc = "C:\\Users\\Parthmaheswari\\Documents\\c language\\Minor2\\Resume\\" + rno + ".txt";
                    inFile.open(open_loc.c_str());
                    if (!inFile) {
                        cout << "Unable to open file " << rno << ".txt";
                        exit(1);   // call system to stop
                    }
                    int wcount = 0;
                    while (inFile.eof() == 0 && wcount < 40) {
                        inFile >> x;
                        cout << x << " ";
                        wcount++;
                    }
                    inFile.close();

                }

                case (4) : {
                    qstate = mysql_query(conn, "select * from recruitment_info");

                    if (!qstate) {
                        res = mysql_store_result(conn);
                        while (row = mysql_fetch_row(res)) {
                            cout << "name: " << row[0] << " "
                                 << "age: " << row[1] << " "
                                 << "phone: " << row[2] << " "
                                 << "email: " << row[3] << " "
                                 << "id: " << row[4] << endl;
                        }
                    } else
                        cout << "query error: " << mysql_error(conn) << endl;
                }

                case (5) : {
                    int i = 0, j = 0, ns, wf = 0, num_rows,
                            total_words = 0, flag = 1, temp;
                    float tf, idf;
                    ifstream inFile;
                    char skills[10][5];
                    float tf_arr[10];
                    string tf_roll [10];
                    char x[40];
                    string myrow, pros_resume_name, resume_name, temp2;
                    string lang, open_loc;
                    cout << "Enter number of skills you are interested in\n";
                    cin >> ns;
                    cout << "Enter the skills\n";
                    for (i = 0; i < ns; i++) {
                        cin >> skills[i];
                    }

                    qstate = mysql_query(conn, "SELECT COUNT(Resume) FROM recruitment_info");

                    if (!qstate) {
                        res = mysql_store_result(conn);
                        row = mysql_fetch_row(res);
                        myrow = row[0];
                        num_rows = (int) myrow[0] - 48;
                        //cout << endl << " NUM Rows =  " << num_rows<< endl;
                    } else
                        cout << "query error: " << mysql_error(conn) << endl;


                    qstate = mysql_query(conn, "SELECT Resume,ProcessedResume FROM recruitment_info");

                    if (!qstate) {
                        res = mysql_store_result(conn);
                        while (row = mysql_fetch_row(res)) {
                            //cout<<row[0]<<endl;
                            resume_name = row[0];                   // get the Resume Name
                            pros_resume_name = row[1];              // get the Processed Resume Name
                            open_loc = pros_resume_name + ".txt";
                            //cout<<open_loc<<endl;
                            inFile.open(open_loc.c_str());
                            if (!inFile) {
                                cout << "Unable to open file";
                                exit(1);   // call system to stop
                            }
                            while (inFile.eof() == 0) {
                                inFile >> x;
                                total_words++;
                                for (int k = 0; k < ns; k++) {
                                    if (strcmp(skills[k], x) == 0) {
                                        wf++;
                                    }
                                }
                            }
                            tf = (wf * 1.0) / (total_words * 1.0);
                            tf_arr[j] = tf;
                            tf_roll[j] =  resume_name;
                            inFile.close();
                            j++;
                        }

                        for (i = 1; (i <= num_rows) && flag; i++) {  // SORTING
                            flag = 0;
                            for (j = 0; j < (num_rows - 1); j++) {
                                if (tf_arr[j + 1] > tf_arr[j])      // ascending order simply changes to <
                                {
                                    // swap elements
                                    temp = tf_arr[j]; temp2 = tf_roll[j];
                                    tf_arr[j] = tf_arr[j + 1]; tf_roll[j] = tf_roll[j + 1];
                                    tf_arr[j + 1] = temp; tf_roll[j+1] = temp2;
                                    flag = 1;               // indicates that a swap occurred.
                                }
                            }
                        }
                        for (i = 0; i < num_rows; i++) {
                            cout << endl << "resume : " << tf_roll[i] << " scored : " << tf_arr[i] << endl;
                        }

                    } else
                        cout << "query error: " << mysql_error(conn) << endl;
                }

                    /*case (6) :
                    {
                        string rno;
                        char present;
                        cout<<"Enter Resume name/Enrollment ID"<<endl;
                        cin>>rno;
                        worker.StopWord(rno);
                    }*/
            }
        } else
            cout << "connection problem: " << mysql_error(conn) << endl;

        cout << endl <<endl << endl <<"Do you want to continue ? (Y/N)";
        cin >> cont;
    }while( cont == 'y' || cont == 'Y');

    return 0;

}
