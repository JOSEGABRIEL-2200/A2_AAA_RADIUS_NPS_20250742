# =====================================================================
# SRV_AD_NPS.ps1 - Asignacion 2 - AAA con RADIUS (NPS)
# Jose Gabriel Feliz Maria - 2025-0742
#
# Windows Server 2022 (WIN-3PRJM03EJ6S.jose.gabriel), controlador del
# dominio jose.gabriel, IP 10.7.42.130/29, gateway 10.7.42.129 (R1).
# Rol NPS (Network Policy and Access Services) como servidor RADIUS
# de R1 y SW1.
# No contiene contrasenas ni el secreto RADIUS: se piden al ejecutar.
# =====================================================================

# ---------- PARTE 1: Active Directory (OU, grupos y usuarios) ----------
# Un grupo por nivel de privilegio que pide la practica (0, 5 y 10),
# con un usuario en cada grupo. Las claves se escriben al ejecutar.
& {
  $ErrorActionPreference = 'Stop'
  Import-Module ActiveDirectory
  $dom = 'DC=jose,DC=gabriel'
  $ou  = "OU=AAA_Red,$dom"
  if (-not (Get-ADOrganizationalUnit -Filter "Name -eq 'AAA_Red'")) {
    New-ADOrganizationalUnit -Name 'AAA_Red' -Path $dom -Description 'Practica AAA: acceso a R1 y SW1 por RADIUS'
  }
  foreach ($n in 0,5,10) {
    if (-not (Get-ADGroup -Filter "Name -eq 'GRP_NIVEL_$n'")) {
      New-ADGroup -Name "GRP_NIVEL_$n" -GroupScope Global -GroupCategory Security -Path $ou -Description "Acceso a R1 y SW1 con privilegio $n"
    }
    if (-not (Get-ADUser -Filter "SamAccountName -eq 'usuario$n'")) {
      $pw = Read-Host -AsSecureString "Clave para usuario$n"
      New-ADUser -Name "usuario$n" -SamAccountName "usuario$n" -UserPrincipalName "usuario$n@jose.gabriel" -Path $ou -AccountPassword $pw -Enabled $true -PasswordNeverExpires $true -Description "Acceso a R1 y SW1 con privilegio $n"
    }
    Add-ADGroupMember -Identity "GRP_NIVEL_$n" -Members "usuario$n"
  }
  Get-ADUser -Filter * -SearchBase $ou -Properties MemberOf |
    Select-Object SamAccountName, Enabled, @{n='Grupo';e={($_.MemberOf | ForEach-Object { ($_ -split ',')[0] -replace 'CN=' }) -join ', '}} |
    Format-Table -AutoSize | Out-String
}

# ---------- PARTE 2: NPS (registro, clientes RADIUS y auditoria) ----------
# R1 envia RADIUS desde 10.7.42.129 (e0/0.20) y SW1 desde 10.7.42.138 (Vlan99).
& {
  $ErrorActionPreference = 'Stop'
  netsh ras add registeredserver
  $ss = Read-Host -AsSecureString 'Secreto RADIUS compartido (el mismo ira en R1 y SW1)'
  $s  = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($ss))
  New-NpsRadiusClient -Name 'R1'  -Address '10.7.42.129' -SharedSecret $s | Out-Null
  New-NpsRadiusClient -Name 'SW1' -Address '10.7.42.138' -SharedSecret $s | Out-Null
  auditpol /set /subcategory:"Network Policy Server" /success:enable /failure:enable
  Get-NpsRadiusClient | Format-Table Name, Address, Enabled -AutoSize | Out-String
}
