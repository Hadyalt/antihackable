import os
from DbContext.encrypted_logger import EncryptedLogger
from DbContext.backup_utils import create_backup, list_backups, restore_backup, delete_backup
from .backup_utils import (
    add_restore_code, revoke_restore_code, validate_restore_code, get_system_admins, get_decrypted_backups
)


def backup_menu(role, username=None):
    logger = EncryptedLogger()
    while True:
        print("\n=== BACKUP & RESTORE MENU ===")
        print("[1] Create Backup")
        print("[2] List Backups")
        print("[3] Restore Backup")
        print("[4] Delete Backup")
        if role == "superadmin":
            print("[5] Generate Restore-Code for System Admin")
            print("[6] Revoke Restore-Code")
            print("[7] Exit Backup Menu")
            valid_choices = ["1", "2", "3", "4", "5", "6", "7"]
        else:
            print("[5] Exit Backup Menu")
            valid_choices = ["1", "2", "3", "4", "5"]
        choice = input("Enter your choice: ").strip()
        if choice not in valid_choices:
            print("Invalid choice. Please enter a valid option.")
            logger.log_entry(username or "system", "Backup Menu", f"Invalid menu choice: {choice}", "No")
            continue
        if choice == "1":
            backup_path = create_backup(username)
            print(f"Backup created: {backup_path}")
            logger.log_entry(username or "system", "Backup Menu", f"Created backup: {backup_path}", "No")
            if role == "systemadmin":
                print("please contact a Super Admin to add a recovery code for this backup.")
            if role == "superadmin":
                while True:
                    add_code = input("Do you want to add a recovery code for a System Admin? (yes/no): ").strip().lower()
                    if add_code not in ["yes", "no"]:
                        print("Invalid input. Please enter 'yes' or 'no'.")
                        logger.log_entry(username or "system", "Backup Menu", f"Invalid input for add recovery code: {add_code}", "No")
                        continue
                    if add_code == "no":
                        logger.log_entry(username or "system", "Backup Menu", "Chose not to add recovery code after backup.", "No")
                        break
                    admins = get_system_admins()
                    if not admins:
                        print("No active System Admins found.")
                        logger.log_entry(username or "system", "Backup Menu", "No active System Admins found for recovery code.", "No")
                        break
                    while True:
                        print("System Admins:")
                        for idx, admin in enumerate(admins, 1):
                            print(f"{idx}. {admin}")
                        sel = input("Select System Admin number: ").strip()
                        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(admins):
                            print("Invalid selection. Please enter a valid number.")
                            logger.log_entry(username or "system", "Backup Menu", f"Invalid System Admin selection: {sel}", "No")
                            continue
                        sel_idx = int(sel) - 1
                        try:
                            code = add_restore_code(os.path.basename(backup_path), admins[sel_idx])
                            if code:
                                print(f"Restore code for {admins[sel_idx]} and backup {os.path.basename(backup_path)}: {code}")
                                logger.log_entry(username or "system", "Backup Menu", f"Generated restore code for {admins[sel_idx]} and backup {os.path.basename(backup_path)}", "No")
                            break
                        except Exception as e:
                            print(f"Failed to generate restore code: {e}")
                            logger.log_entry(username or "system", "Backup Menu", f"Failed to generate restore code: {e}", "Yes")
                    break
        elif choice == "2":
            backups = list_backups()
            logger.log_entry(username or "system", "Backup Menu", "Listed backups", "No")
            if backups:
                print("Available backups:")
                for b in backups:
                    print(f"- {b}")
            else:
                print("No backups found.")
        elif choice == "3":
            backups = list_backups()
            if not backups:
                print("No backups to restore.")
                logger.log_entry(username or "system", "Backup Menu", "No backups to restore.", "No")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number to restore: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    logger.log_entry(username or "system", "Backup Menu", f"Invalid restore selection: {sel}", "No")
                    continue
                sel_idx = int(sel) - 1
                if role == "systemadmin":
                    code = input("Enter your restore code: ").strip()
                    if not validate_restore_code(backups[sel_idx], username, code):
                        print("Invalid or already used restore code.")
                        logger.log_entry(username or "system", "Backup Menu", f"Invalid or used restore code for {backups[sel_idx]}", "Yes")
                        continue
                try:
                    restore_backup(backups[sel_idx], username)
                    print("Restore complete. Please restart the application.")
                    logger.log_entry(username or "system", "Backup Menu", f"Restored backup: {backups[sel_idx]}", "No")
                    exit()
                except Exception as e:
                    print(f"Restore failed: {e}")
                    logger.log_entry(username or "system", "Backup Menu", f"Restore failed: {e}", "Yes")
                break
        elif choice == "4":
            backups = list_backups()
            if not backups:
                print("No backups to delete.")
                logger.log_entry(username or "system", "Backup Menu", "No backups to delete.", "No")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number to delete: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    logger.log_entry(username or "system", "Backup Menu", f"Invalid delete selection: {sel}", "No")
                    continue
                sel_idx = int(sel) - 1
                try:
                    delete_backup(backups[sel_idx], username)
                    print(f"Backup deleted: {backups[sel_idx]}")
                    logger.log_entry(username or "system", "Backup Menu", f"Deleted backup: {backups[sel_idx]}", "No")
                except Exception as e:
                    print(f"Delete failed: {e}")
                    logger.log_entry(username or "system", "Backup Menu", f"Delete failed: {e}", "Yes")
                break
        elif role == "superadmin" and choice == "5":
            backups = list_backups()
            if not backups:
                print("No backups available.")
                logger.log_entry(username or "system", "Backup Menu", "No backups available for restore code generation.", "No")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    logger.log_entry(username or "system", "Backup Menu", f"Invalid backup selection for code: {sel}", "No")
                    continue
                sel_idx = int(sel) - 1
                admins = get_system_admins()
                if not admins:
                    print("No active System Admins found.")
                    logger.log_entry(username or "system", "Backup Menu", "No active System Admins found for code generation.", "No")
                    break
                while True:
                    print("System Admins:")
                    for idx, admin in enumerate(admins, 1):
                        print(f"{idx}. {admin}")
                    admin_sel = input("Select System Admin number: ").strip()
                    if not admin_sel.isdigit() or int(admin_sel) < 1 or int(admin_sel) > len(admins):
                        print("Invalid selection. Please enter a valid number.")
                        logger.log_entry(username or "system", "Backup Menu", f"Invalid System Admin selection for code: {admin_sel}", "No")
                        continue
                    admin_idx = int(admin_sel) - 1
                    try:
                        code = add_restore_code(backups[sel_idx], admins[admin_idx])
                        if code:
                            print(f"Restore code for {admins[admin_idx]} and backup {backups[sel_idx]}: {code}")
                            logger.log_entry(username or "system", "Backup Menu", f"Generated restore code for {admins[admin_idx]} and backup {backups[sel_idx]}", "No")
                        break
                    except Exception as e:
                        print(f"Failed to generate restore code: {e}")
                        logger.log_entry(username or "system", "Backup Menu", f"Failed to generate restore code: {e}", "Yes")
                break
        elif role == "superadmin" and choice == "6":
            backups = list_backups()
            if not backups:
                print("No backups available.")
                logger.log_entry(username or "system", "Backup Menu", "No backups available for revoke.", "No")
                continue
            while True:
                print("Available backups:")
                for idx, b in enumerate(backups, 1):
                    print(f"{idx}. {b}")
                sel = input("Select backup number: ").strip()
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(backups):
                    print("Invalid selection. Please enter a valid number.")
                    logger.log_entry(username or "system", "Backup Menu", f"Invalid backup selection for revoke: {sel}", "No")
                    continue
                sel_idx = int(sel) - 1
                admins = get_system_admins()
                if not admins:
                    print("No active System Admins found.")
                    logger.log_entry(username or "system", "Backup Menu", "No active System Admins found for revoke.", "No")
                    break
                while True:
                    print("System Admins:")
                    for idx, admin in enumerate(admins, 1):
                        print(f"{idx}. {admin}")
                    admin_sel = input("Select System Admin number: ").strip()
                    if not admin_sel.isdigit() or int(admin_sel) < 1 or int(admin_sel) > len(admins):
                        print("Invalid selection. Please enter a valid number.")
                        logger.log_entry(username or "system", "Backup Menu", f"Invalid System Admin selection for revoke: {admin_sel}", "No")
                        continue
                    admin_idx = int(admin_sel) - 1
                    try:
                        if revoke_restore_code(backups[sel_idx], admins[admin_idx]):
                            print(f"Restore code for {admins[admin_idx]} and backup {backups[sel_idx]} revoked.")
                            logger.log_entry(username or "system", "Backup Menu", f"Revoked restore code for {admins[admin_idx]} and backup {backups[sel_idx]}", "No")
                        else:
                            print("No active restore code found to revoke.")
                            logger.log_entry(username or "system", "Backup Menu", f"No active restore code found to revoke for {admins[admin_idx]} and backup {backups[sel_idx]}", "No")
                        break
                    except Exception as e:
                        print(f"Failed to revoke restore code: {e}")
                        logger.log_entry(username or "system", "Backup Menu", f"Failed to revoke restore code: {e}", "Yes")
                break
        elif (role == "superadmin" and choice == "7") or (role != "superadmin" and choice == "5"):
            logger.log_entry(username or "system", "Backup Menu", "Exited backup menu.", "No")
            return
        else:
            print("Invalid choice.")
            logger.log_entry(username or "system", "Backup Menu", f"Invalid menu choice (else): {choice}", "No")
