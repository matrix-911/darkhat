from flask import Blueprint, request, jsonify, send_file
from .generator import generate_passwords_from_rule, parse_rule, parse_date, generate_numbers_from_date
import os

api_bp = Blueprint("api", __name__)

@api_bp.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data or "strings" not in data or not isinstance(data["strings"], list) or len(data["strings"]) == 0:
        return jsonify({"error": "Missing or invalid 'strings'. You must provide at least one."}), 400

    if "numbers" in data and not isinstance(data["numbers"], list):
        return jsonify({"error": "'numbers' must be a list if provided."}), 400

    if "dates" in data and not isinstance(data["dates"], list):
        return jsonify({"error": "'dates' must be a list if provided."}), 400

    strings = data.get("strings", [])
    numbers = data.get("numbers", [])
    dates = data.get("dates", [])
    min_length = data.get("min_length", 1)
    max_length = data.get("max_length", None)
    password_limit = data.get("password_limit", 1000000)

    rules_path = "rules/rules.txt"
    output_path = "output/passwords.txt"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(rules_path, "r", encoding="utf-8") as f:
        rules = [line.strip() for line in f if line.strip()]

    symbols = ["@", "#", "$", "%", "!", "&", "*", "-", "_"]
    common_numbers = [
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
        "123", "1234", "12345", "123456",
        "321", "4321", "54321",
        "123321", "12344321", "1234554321",
        "2020", "2021", "2022", "2023", "2024", "2025"
    ]

    date_info_list = [{
        'components': parse_date(d),
        'numbers': generate_numbers_from_date(d)
    } for d in dates]

    total_written = 0
    preview_passwords = []

    with open(output_path, "w", encoding="utf-8") as outfile:
        for rule_str in rules:
            if total_written >= password_limit:
                break

            rule = parse_rule(rule_str)
            has_spaces = " + " in rule_str and "literal: " in rule_str

            passwords = generate_passwords_from_rule(
                rule, strings, numbers, date_info_list,
                symbols=symbols, common_numbers=common_numbers, has_spaces=has_spaces
            )

            for pwd in passwords:
                if total_written >= password_limit:
                    break
                if min_length and len(pwd) < min_length:
                    continue
                if max_length and len(pwd) > max_length:
                    continue

                outfile.write(pwd + "\n")
                if len(preview_passwords) < 100:
                    preview_passwords.append(pwd)
                total_written += 1

    return jsonify({
        "count": total_written,
        "preview": preview_passwords
    })

@api_bp.route("/download", methods=["GET"])
def download_passwords():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(base_dir, "output", "passwords.txt")

    if not os.path.exists(output_path):
        return jsonify({"error": "No password file found."}), 404

    return send_file(output_path, as_attachment=True, download_name="passwords.txt")
