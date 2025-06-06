import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from ssh_service import SSHService


# Crear o conectar a la base de datos
conn = sqlite3.connect('dispositivos.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dispositivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ip TEXT NOT NULL,
        usuario TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# Funciones de ABM
def alta_dispositivo():
    nombre = simpledialog.askstring("Alta", "Ingrese el nombre del dispositivo:")
    ip = simpledialog.askstring("Alta", "Ingrese la IP del dispositivo:")
    usuario = simpledialog.askstring("Alta", "Ingrese el usuario del dispositivo:")
    password = simpledialog.askstring("Alta", "Ingrese el password del dispositivo:")
    if nombre and ip and usuario and password:
        cursor.execute("INSERT INTO dispositivos (nombre, ip, usuario, password) VALUES (?, ?, ?, ?)",
                       (nombre, ip, usuario, password))
        conn.commit()
        messagebox.showinfo("Alta", "Dispositivo agregado exitosamente.")
        listar_dispositivos()

def baja_dispositivo():
    id_disp = simpledialog.askinteger("Baja", "Ingrese el ID del dispositivo a eliminar:")
    cursor.execute("DELETE FROM dispositivos WHERE id=?", (id_disp,))
    conn.commit()
    messagebox.showinfo("Baja", "Dispositivo eliminado (si existía).")
    listar_dispositivos()

def modificar_dispositivo():
    id_disp = simpledialog.askinteger("Modificación", "Ingrese el ID del dispositivo a modificar:")
    cursor.execute("SELECT * FROM dispositivos WHERE id=?", (id_disp,))
    row = cursor.fetchone()
    if row:
        nuevo_nombre = simpledialog.askstring("Modificar", "Nombre actual: {}\nNuevo nombre:".format(row[1]), initialvalue=row[1])
        nueva_ip = simpledialog.askstring("Modificar", "IP actual: {}\nNueva IP:".format(row[2]), initialvalue=row[2])
        nuevo_usuario = simpledialog.askstring("Modificar", "Usuario actual: {}\nNuevo usuario:".format(row[3]), initialvalue=row[3])
        nuevo_password = simpledialog.askstring("Modificar", "Password actual: {}\nNuevo password:".format(row[4]), initialvalue=row[4])
        cursor.execute("UPDATE dispositivos SET nombre=?, ip=?, usuario=?, password=? WHERE id=?",
                       (nuevo_nombre, nueva_ip, nuevo_usuario, nuevo_password, id_disp))
        conn.commit()
        messagebox.showinfo("Modificar", "Dispositivo modificado exitosamente.")
        listar_dispositivos()
    else:
        messagebox.showerror("Error", "No se encontró un dispositivo con ese ID.")

def listar_dispositivos():
    for i in tree.get_children():
        tree.delete(i)
    cursor.execute("SELECT * FROM dispositivos")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

def probar_conexion_ssh():
    id_disp = simpledialog.askinteger("SSH", "Ingrese el ID del dispositivo a conectar:")
    cursor.execute("SELECT ip, usuario, password FROM dispositivos WHERE id=?", (id_disp,))
    row = cursor.fetchone()
    if row:
        ip, usuario, password = row
        ssh = SSHService(ip, usuario, password)
        if ssh.conectar():
            comando = simpledialog.askstring("Comando", "Ingrese el comando a ejecutar:")
            salida, errores = ssh.ejecutar_comando(comando)
            messagebox.showinfo("Resultado", f"Salida:\n{salida}\nErrores:\n{errores}")
            ssh.cerrar()
        else:
            messagebox.showerror("Error", "No se pudo conectar por SSH.")
    else:
        messagebox.showerror("Error", "ID no encontrado.")


# Interfaz gráfica (Tkinter)
root = tk.Tk()
root.title("ABM Dispositivos de Red")

btn_alta = tk.Button(root, text="Alta", command=alta_dispositivo)
btn_alta.pack(pady=5)

btn_baja = tk.Button(root, text="Baja", command=baja_dispositivo)
btn_baja.pack(pady=5)

btn_modificar = tk.Button(root, text="Modificar", command=modificar_dispositivo)
btn_modificar.pack(pady=5)

btn_listar = tk.Button(root, text="Listar", command=listar_dispositivos)
btn_listar.pack(pady=5)

btn_ssh = tk.Button(root, text="Probar SSH", command=probar_conexion_ssh)
btn_ssh.pack(pady=5)


tree = ttk.Treeview(root, columns=("ID", "Nombre", "IP", "Usuario", "Password"), show="headings")
for col in ("ID", "Nombre", "IP", "Usuario", "Password"):
    tree.heading(col, text=col)
tree.pack(pady=10)

listar_dispositivos()

root.mainloop()

# Cerrar conexión
conn.close()
