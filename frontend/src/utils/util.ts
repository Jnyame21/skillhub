import { useUserAuthStore } from "@/stores/userAuthStore";

export const parseTime = (timeString: string)=> {
  const [hours, minutes] = timeString.split(":").map(Number);
  const time = new Date();
  time.setHours(hours, minutes, 0, 0);
  return time;
}

export const isStrongPassword = (password:string)=>{
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (password.length < minLength) {
    return { strong: false, message: "Password must be at least 8 characters long" };
  }
  if (!hasUpperCase) {
    return { strong: false, message: "Password must include at least one uppercase letter" };
  }
  if (!hasLowerCase) {
    return { strong: false, message: "Password must include at least one lowercase letter" };
  }
  if (!hasNumber) {
    return { strong: false, message: "Password must include at least one number" };
  }
  if (!hasSpecialChar) {
    return { strong: false, message: "Password must include at least one special character" };
  }

  return { strong: true, message: "Password is strong!" };
}

export const  formatTime = (timeString:string)=> {
  let hours = timeString.split(":").map(Number)[0];
  const minutes = timeString.split(":").map(Number)[1]
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;

  return `${hours}:${minutes.toString().padStart(2, "0")} ${ampm}`;
}

export const  formatDate = (dateString:string, format_type: string)=> {
  const date = new Date(dateString);
  let dayAbbrev = ''
  let monthAbbrev = ''
  if (format_type === 'short'){
    dayAbbrev = date.toLocaleString("default", { weekday: "short" }).toUpperCase();
    monthAbbrev = date.toLocaleString("default", { month: "short" }).toUpperCase();
  }
  else if (format_type === 'long'){
    dayAbbrev = date.toLocaleString("default", { weekday: "long" }).toUpperCase();
    monthAbbrev = date.toLocaleString("default", { month: "long" }).toUpperCase();
  }
  const day = date.getDate();

  return `${dayAbbrev}(${monthAbbrev} ${day})`;
}

export const parseFormattedDate = (formattedDate: string): string => {
  const userAuthStore = useUserAuthStore()
  const match = formattedDate.match(/\((\w+)\s(\d+)\)/);
  if (!match) {
    throw new Error("Invalid date format");
  }
  const [, monthAbbrev, day] = match;
  const dateObj = new Date(`${monthAbbrev} ${day}, ${new Date(userAuthStore.currentDate).getFullYear()}`);
  const year = dateObj.getFullYear();
  const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
  const dayNum = day.padStart(2, "0");
  return `${year}-${month}-${dayNum}`;
};
