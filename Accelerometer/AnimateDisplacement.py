import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv 

fig = plt.figure()
#plt.title("Compressions")
ax1 = fig.add_subplot(1, 1, 1)

def animate(i):
    with open('data.csv') as csv_file:
        
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        
        xs = []
        ys = []
        
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                #x, y = row.split(',')
                
                #print(row)

                xs.append(float(row[0]))
                ys.append(float(row[2]))
                
                line_count += 1

        #lines = graph_data.split('\n')

        #for line in lines:
        #    if line == lines[0]:
        #        pass
        #    elif len(line) > 1:

        #        x, y = line.split(',')

      #          xs.append(float(x))
       #         ys.append(float(y))
               
    ax1.clear()
    ax1.plot(xs, ys)
    
    plt.title('Compressions')
    plt.xlabel('Time')
    plt.ylabel('Depth')

ani = animation.FuncAnimation(fig, animate)
plt.show()
"""
#create csv file to save the data
file = open("data.csv", "a")

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []


def animate(i, xs, ys):
    # Add x and y to lists
    xs.append(dt.now().strftime('%H:%M:%S.%f'))
    ys.append(float(accel_data['z']))
    
    # Limit x and y lists to 20 items
    xs = xs[-10:]
    ys = ys[-10:]
    
    time.sleep(0.01)

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('MPU6050 Acceleration over Time')
    plt.ylabel('-Acceleration')

#show real-time graph
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
plt.show()
"""
