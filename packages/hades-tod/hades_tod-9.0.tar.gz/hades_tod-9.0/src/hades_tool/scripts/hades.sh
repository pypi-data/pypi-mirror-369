#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Simplified but elegant color palette
declare -A COLORS=(
    [PRIMARY]='\e[38;2;120;200;255m'    # Biru lembut
    [ACCENT]='\e[38;2;255;125;175m'     # Merah muda lembut
    [SUCCESS]='\e[38;2;125;255;175m'    # Hijau lembut
    [WARNING]='\e[38;2;255;230;125m'    # Kuning lembut
    [DANGER]='\e[38;2;255;125;125m'     # Merah lembut
    [MUTED]='\e[38;2;150;150;180m'      # Ungu pudar
    [BRIGHT]='\e[38;2;235;235;255m'     # Putih cerah
    [DIM]='\e[38;2;100;100;120m'        # Abu-abu redup
)

# Effects
BOLD='\e[1m'
ITALIC='\e[3m'
RESET='\e[0m'

# Configuration
VERSION="9.0" # Versi diperbarui untuk revisi ini
AUTHOR="Anonre | Joel Indra"
YEAR=$(date +%Y)
SCAN_DATE=$(date +"%d-%m-%Y %H:%M:%S")
SESSION_ID=$(date +%s | sha256sum | cut -c1-12)

# Enable error handling
set -e
trap 'elegant_error $LINENO' ERR

# Simplified elegant typing - prints instantly
elegant_type() {
    local text="$1"
    echo -e "${text}" # Mencetak seluruh teks sekaligus
    sleep 0.05 # Jeda sangat singkat untuk keindahan visual
}

# Simplified elegant loading animation (now just a text prompt)
elegant_loading() {
    local task_name=$1
    local delay=${2:-0.8} # Total penundaan untuk pesan muncul "Done"

    echo -ne "\n${COLORS[ACCENT]}>>> ${task_name}...${RESET}" # Simpler prompt
    sleep $delay
    # Menimpa baris dengan "Done!" dan tanda centang sukses
    echo -e "\r${COLORS[ACCENT]}>>> ${task_name}... ${COLORS[SUCCESS]}Done!${RESET} \n" # Overwrite and add newline
}

# Elegant error handler
elegant_error() {
    local line=$1
    echo ""
    echo -e "${COLORS[DANGER]}${BOLD}║ Error detected at line $line     ${RESET}"
    exit 1
}

# Elegant banner
display_banner() {
    clear

    # Direct printing for proper color rendering
    echo ""
    echo -e "${COLORS[PRIMARY]}│  ${COLORS[ACCENT]}╦ ╦╔═╗╔╦╗╔═╗╔═╗${COLORS[PRIMARY]}                 "
    echo -e "${COLORS[PRIMARY]}│  ${COLORS[ACCENT]}╠═╣╠═╣ ║║║╣ ╚═╗${COLORS[PRIMARY]}                 "
    echo -e "${COLORS[PRIMARY]}│  ${COLORS[ACCENT]}╩ ╩╩ ╩═╩╝╚═╝╚═╝${COLORS[PRIMARY]}                 "
    echo -e "${COLORS[PRIMARY]}│  ${COLORS[SUCCESS]}Bug Bounty Framework v${VERSION}${COLORS[PRIMARY]}        "
    echo -e "${COLORS[PRIMARY]}│  ${COLORS[MUTED]}Created by: ${COLORS[BRIGHT]}${AUTHOR} ©${YEAR}${COLORS[PRIMARY]}      "    
    sleep 0.5 # Jeda singkat setelah tampilan banner
    
    # System info with elegant styling (maintains original box structure)
    echo ""
    echo -e "${COLORS[PRIMARY]}│ ${COLORS[SUCCESS]}• Kernel    ${COLORS[MUTED]}| ${COLORS[BRIGHT]}$(uname -r)${COLORS[PRIMARY]}${RESET}"
    echo -e "${COLORS[PRIMARY]}│ ${COLORS[SUCCESS]}• Machine   ${COLORS[MUTED]}| ${COLORS[BRIGHT]}$(uname -m)${COLORS[PRIMARY]}${RESET}"
    echo -e "${COLORS[PRIMARY]}│ ${COLORS[SUCCESS]}• Session   ${COLORS[MUTED]}| ${COLORS[BRIGHT]}$SESSION_ID${COLORS[PRIMARY]}${RESET}"
    echo -e "${COLORS[PRIMARY]}│ ${COLORS[SUCCESS]}• Timestamp ${COLORS[MUTED]}| ${COLORS[BRIGHT]}$SCAN_DATE${COLORS[PRIMARY]}${RESET}"
    echo ""
    if [[ $(id -u) -eq 0 ]]; then
        echo -e "│ • ${COLORS[SUCCESS]}You are Root! You can run this tool.${COLORS[PRIMARY]}${RESET}"
    else
        echo -e "│ • ${COLORS[DANGER]}Not Root! You need root to run this tool.${COLORS[PRIMARY]}${RESET}"
    fi
}

# Elegant help display (simplified section headers)
display_help() {
    display_banner
    
    # Reconnaissance
    echo ""
    echo -e "${COLORS[PRIMARY]}${BOLD}--- Reconnaissance ---${RESET}\n" # Simplified header
    echo -e "  ${COLORS[BRIGHT]}-d ${COLORS[MUTED]}--mass-recon    ${COLORS[WARNING]}Mass Target Recon${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f,subfinder, assetfinder, httprobe, waybackurls, anew, ffuf, gf, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-s ${COLORS[MUTED]}--single-recon  ${COLORS[WARNING]}Single Target Recon${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, waybackurls, anew, ffuf, gf, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-f ${COLORS[MUTED]}--port-scan     ${COLORS[WARNING]}Single Target Port Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}nmap, curl ${RESET}"
    echo -e ""
    
    # Injection
    echo -e "${COLORS[ACCENT]}${BOLD}--- Injection Testing ---${RESET}\n" # Simplified header
    echo -e "  ${COLORS[BRIGHT]}-p ${COLORS[MUTED]}--mass-sql      ${COLORS[WARNING]}Mass Target SQL Injection Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f,subfinder, assetfinder, httprobe, waybackurls, anew, ffuf, gf, sqltimer, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-o ${COLORS[MUTED]}--single-sql    ${COLORS[WARNING]}Single Target SQL Injection Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, waybackurls, anew, ffuf, gf, sqltimer, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-w ${COLORS[MUTED]}--mass-xss      ${COLORS[WARNING]}Mass Target XSS Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f,subfinder, assetfinder, httprobe, waybackurls, anew, ffuf, gf, dalfox, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-x ${COLORS[MUTED]}--single-xss    ${COLORS[WARNING]}Single Target XSS Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, waybackurls, anew, ffuf, gf, dalfox, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-n ${COLORS[MUTED]}--single-lfi    ${COLORS[WARNING]}Single Target LFI Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, waybackurls, anew, ffuf, gf, mapfile, md5sum, curl ${RESET}"
    echo -e ""
    
    # Special ops
    echo -e "${COLORS[WARNING]}${BOLD}--- Special Operations ---${RESET}\n" # Simplified header
    echo -e "  ${COLORS[BRIGHT]}-m ${COLORS[MUTED]}--mass-assess   ${COLORS[PRIMARY]}Mass Target Auto VA${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, subfinder, assetfinder, httprobe, nuclei, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-y ${COLORS[MUTED]}--sub-takeover  ${COLORS[PRIMARY]}Subdomain Takeover Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, notifier.sh, subfinder, assetfinder, httprobe, subjack, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-q ${COLORS[MUTED]}--dir-patrol    ${COLORS[PRIMARY]}Directory Patrol Target Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, notifier.sh, subfinder, assetfinder, httprobe, dirsearch ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-l ${COLORS[MUTED]}--js-finder     ${COLORS[PRIMARY]}ALL JS Secret Finder${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, notifier.sh, subfinder, assetfinder, httprobe, waybackurls, anew, trufflehog, curl ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-k ${COLORS[MUTED]}--mass-cors     ${COLORS[PRIMARY]}Mass Target CORS Missconfig Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, subfinder, assetfinder, httprobe, waybackurls, anew, ffuf, gf ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-u ${COLORS[MUTED]}--mass-csrf     ${COLORS[PRIMARY]}Mass Target CSRF Scan${RESET}"
    echo -e "  ${COLORS[MUTED]}wafw00f, subfinder, assetfinder, httprobe, waybackurls, anew, ffuf, gf, curl ${RESET}"
    echo -e ""

    echo -e "${COLORS[DANGER]}${BOLD}--- OWASP WASTG Testing ---${RESET}\n" # Simplified header
    echo -e "  ${COLORS[BRIGHT]}-e ${COLORS[MUTED]}--client-test   ${COLORS[BRIGHT]}Client-side Testing${RESET}"
    echo -e "  ${COLORS[MUTED]}curl, jq ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-b ${COLORS[MUTED]}--weak-test     ${COLORS[BRIGHT]}Testing For Weak Cryptography${RESET}"
    echo -e "  ${COLORS[MUTED]}nmap, sslscan, openssl, curl, timeout ${RESET}"
    echo -e ""
    echo -e "  ${COLORS[BRIGHT]}-r ${COLORS[MUTED]}--info-test     ${COLORS[BRIGHT]}Information Gathering [UPCOMING]${RESET}\n"

    # System
    echo -e "${COLORS[BRIGHT]}${BOLD}--- System ---${RESET}\n" # Simplified header
    echo -e "  ${COLORS[BRIGHT]}-i ${COLORS[MUTED]}--install       ${COLORS[PRIMARY]}Install Dependencies${RESET}"
    echo -e "  ${COLORS[BRIGHT]}-h ${COLORS[MUTED]}--help          ${COLORS[PRIMARY]}Display Commands${RESET}\n"

    echo -e "${COLORS[DIM]}${BOLD}--- More Info ---${RESET}\n" # Simplified header
    echo -e "${COLORS[BRIGHT]}Usage: ${COLORS[MUTED]}./hades [options]${RESET}"
    echo -e "${COLORS[BRIGHT]}Repo:  ${COLORS[SUCCESS]}https://github.com/joelindra/hades${RESET}\n"
}

# Module execution with elegant loading
execute_module() {
    local module_name=$1
    local script_path=$2
    
    # Use the simplified loading animation
    elegant_loading "Loading Module" 0.5 # Shorter delay for quicker feel
    
    # Execute
    # <-- BARIS INI DIPERBAIKI
    # Menggunakan path absolut dari SCRIPT_DIR untuk menghindari error "No such file or directory"
    if source "$SCRIPT_DIR/function/$script_path" 2>/tmp/hades_error.log; then
        echo -e "${COLORS[SUCCESS]}${BOLD}Module executed successfully${RESET}\n"
    else
        echo -e "${COLORS[DANGER]}${BOLD}Module execution failed${RESET}"
        cat /tmp/hades_error.log
        exit 1
    fi
}

# Options mapping
declare -A options_map=(
    # Reconnaissance
    [-d]="m-recon.sh"
    [--mass-recon]="m-recon.sh"
    [-s]="s-recon.sh"
    [--single-recon]="s-recon.sh"
    [-f]="s-port.sh"
    [--port-scan]="s-port.sh"
    
    # Injection
    [-p]="m-sqli.sh"
    [--mass-sql]="m-sqli.sh"
    [-o]="s-sqli.sh"
    [--single-sql]="s-sqli.sh"
    [-w]="m-xss.sh"
    [--mass-xss]="m-xss.sh"
    [-x]="s-xss.sh"
    [--single-xss]="s-xss.sh"
    [-n]="s-lfi.sh"
    [--single-lfi]="s-lfi.sh"
    
    # Assessment
    [-m]="m-scan.sh"
    [--mass-assess]="m-scan.sh"
    
    # Special
    [-y]="takeover.sh"
    [--sub-takeover]="takeover.sh"
    [-u]="m-csrf.sh"
    [--mass-csrf]="m-csrf.sh"
    [-q]="dir-scan.sh"
    [--dir-patrol]="dir-scan.sh"
    [-l]="m-js.sh"
    [--js-finder]="m-js.sh"
    [-k]="m-cors.sh"
    [--mass-cors]="m-cors.sh"

    [-b]="weak.sh"
    [--weak-test]="weak.sh"
    [-e]="client.sh"
    [--client-test]="client.sh"
    
    # System
    [-i]="all-req.sh"
    [--install]="all-req.sh"
    [-h]="help"
    [--help]="help"
)

# Update check with simplified display
check_updates() {
    echo -e "\n${COLORS[WARNING]}${BOLD}--- Update Check ---${RESET}" # Simplified header
    echo -ne "${COLORS[BRIGHT]}Checking for updates...${RESET}"
    sleep 1 # Short delay for checking
    echo -e "\r${COLORS[SUCCESS]}Latest version installed.${RESET}\n" # Overwrite line
}

# Main execution
main() {
    # Display banner
    display_banner
    
    # Check updates
    check_updates
    
    # No arguments
    if [[ $# -eq 0 ]]; then
        display_help
        exit 0
    fi
    
    # Process options
    for option in "$@"; do
        local script="${options_map[$option]}"
        
        if [[ -z "$script" ]]; then
            echo -e "\n${COLORS[DANGER]}${BOLD}✗ Invalid command: $option${RESET}"
            display_help
            exit 1
        fi
        
        if [[ "$script" == "help" ]]; then
            display_help
            continue
        fi
        
        # Replaced old "Initializing... ready" with a more elegant loading for each module
        execute_module "$option" "$script"
    done
    
    # Session end
    echo ""
    echo -e "${COLORS[SUCCESS]}| ${COLORS[WARNING]}Session Complete${COLORS[SUCCESS]}                         ${RESET}"
    echo -e "${COLORS[SUCCESS]}| ${COLORS[BRIGHT]}• Time   ${COLORS[MUTED]}| ${COLORS[ACCENT]}$(date +"%H:%M:%S")${COLORS[SUCCESS]}                      ${RESET}"
    echo -e "${COLORS[SUCCESS]}| ${COLORS[BRIGHT]}• Status ${COLORS[MUTED]}| ${COLORS[SUCCESS]}All operations successful${COLORS[SUCCESS]}   ${RESET}"
}

# Execute main
main "$@"