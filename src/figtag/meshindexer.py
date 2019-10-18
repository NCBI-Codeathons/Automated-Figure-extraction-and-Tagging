import requests
import sys


_API_URL = 'https://ii.nlm.nih.gov/cgi-bin/II/Interactive/interactiveMTI.pl'


def meshindexer(figure_captions_file: str, output_list: str):
    with open(figure_captions_file, "r") as f:
        inputs = f.readlines()

    with open(output_list, "w") as of:
        for input in inputs:
            input = input.rstrip()
            idx, qstr = input.split("\t")
            r = requests.post(_API_URL,
                              data={
                                  'InputText': qstr,
                                  'Filtering': 'default_MTI',
                                  'Output': 'justFacts'})
            if r.status_code == 200:
                of.write(f"{idx}\t{_parse(r.text)}\n")
            else:
                print(f"search failed for {figure_captions_file}.", file=sys.stderr)


def _parse(data):
    out = []
    for line in data.split("\n"):
        fields = line.split("|")
        if len(fields) < 3:
            continue
        out.append(fields[1])
    return '|'.join(out)


"""  # noqa: E501
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Interactive MTI Results</title>
  <style type="text/css">
    td {color:black;font-size:9pt;}
    th {color:white;font-size:9pt;font-weight:bolder;}
    .Cnvtd { color: white; background: red; font-weight: bolder; }
  </style>
</head>

<body bgcolor=white text=black>
<table border=0 cellspacing=0 cellpadding=0 width="100%">
  <tr>
    <td valign=middle align=center>
        <font color="#0033cc" size="+3"><b>
           Interactive MTI Results
        </b></font>
    </td>
  </tr>
</table>

<hr size=3><br>

<b><u>User Information:</u></b> &nbsp;PUBMTI<br><br>
<b><u>Run Time:</u></b> &nbsp;10/17/2019 22:49:40<br><br>
<b><u>Input Text:</u></b><br>

<br>
<table border=1 bgcolor=tan>
  <tr bgcolor=white>
    <td>
      <pre wrap>Blood Platelets, metabolism*, physiology, ultrastructure,Membrane Glycoproteins, blood*, genetics, immunology,P-Selectin, blood*;Animals,Antibodies, Monoclonal,Base Sequence,DNA Primers, genetics,Endothelium, Vascular, physiology,Gene Expression,Humans,Leukocytes, metabolism,Ligands,Male,Mice,Mice, Inbred C57BL,Microscopy, Immunoelectron,Platelet Activation,RNA, Messenger, blood, genetics

</pre>
    </td>
  </tr>
</table>
<br>
<hr>
<b><u>Results:</u></b><br>

<br>
<table border=1 bgcolor=tan>
  <tr bgcolor=white>
    <td>
      <pre wrap>
<b>Command: MTI -default_MTI -justFacts</b>
<b>Version: 2018 Version of MeSH Used to Generate Recommendations
</b><hr>
00000000|Male|C0086582|381145
00000000|Mice|C0026809|381145
00000000|Animals|C0003062|381145
00000000|Humans|C0086418|381145
00000000|SELP protein, human|C2742134|380145
00000000|P-Selectin|C0134835|380144
00000000|Blood Platelets|C0005821|112598
00000000|DNA Primers|C0206416|67462
00000000|Ligands|C0023688|48110
00000000|Membrane Glycoproteins|C0025248|44966
00000000|Base Sequence|C0004793|41483
00000000|RNA|C0035668|33596
00000000|Microscopy|C0026018|33539
00000000|Mice, Inbred C57BL|C0025921|17523
00000000|Platelet Activation|C0032173|158697
00000000|Leukocytes|C0023516|40200
00000000|Antibodies|C0003241|13674
00000000|Endothelium|C0014257|8778
      </pre>
    </td>
  </tr>
</table>
</body>
</html>

</body>
</html>
"""
